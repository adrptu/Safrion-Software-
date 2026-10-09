# -*- coding: utf-8 -*-
"""Teste CDP · CTL-4 (CONTROLE-01, frente C): a demanda líquida é uma só por fazenda e acompanha as O.S. do cenário compartilhado.
Fluxo principal: Planejar safra (etapa 4, passo=demanda) → Compra de insumos (etapa 2, SOL-2026-07) → Mapa › Insumos mostram a mesma conta;
a O.S. muda no cenário (tela O.S.) e a demanda muda junto no Planejar safra e no Mapa, sem redigitar nada; a solicitação já enviada que pede
mais do que a demanda de agora aparece como "Acima da demanda" e o Planejar safra a atualiza (a Compra lê a versão nova).
  normal    · Fungicida A 0 L (a OS-0421 cobre a 1ª aplicação; nunca 145,2 L), MAP 80.000 kg, Ureia 1.140 kg (OS-0418); Mapa com os mesmos números
  recusa    · cancelar a OS-0418 sem motivo é recusado e a demanda não muda; justificativa de proposta mais cara e mais tardia é exigida (DEM-08)
  repetição · recarregar não duplica nem perde nada; cancelar de novo é recusado; atualizar a SOL de novo não muda nada; restaurar a
              demonstração volta aos números da semente
  390 px    · as mesmas leituras no celular, sem rolagem horizontal da página
  revisão do c5d337a · V1/V2 entregar no Estoque não muda a compra (estoque do mesmo cenário); C1/C2 a Compra avisa a SOL acima da
              demanda; Q1/Q2 só gestor ou agrônomo atualiza a SOL e a versão grava quem e quando; P1 pedido emitido antes do complemento
              continua impedindo a redução
Uso: python3 demanda_unica_nav_test.py   (≈ 120 s; capturas q_ctl4_*.png em _probe/)"""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
R=os.path.join(HERE,'_render'); OUT=os.path.join(HERE,'_probe'); os.makedirs(OUT,exist_ok=True)
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
OK=[]; FAIL=[]
def chk(nome,cond,det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ')+nome+('' if cond else f' · {str(det)[:500]}'),flush=True)
c=Chrome(port=free()); J=c.js; B=f'http://127.0.0.1:{p}/'
c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__err=[];addEventListener('error',e=>window.__err.push(String(e.message)));addEventListener('unhandledrejection',e=>window.__err.push(String(e.reason)));"})
ERR=[]
def col():
    try: ERR.extend(J("location.href==='about:blank'?[]:(window.__err||['sem ouvinte em '+location.pathname]).concat([...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText))") or [])
    except Exception as e: ERR.append('coleta: '+str(e))
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
try:
    clk=lambda t,root=None,w=.45: (J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"),time.sleep(w))[0]
    T=lambda: J("[...document.querySelectorAll('[role=status],[role=alert]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    body=lambda: J("document.body.innerText") or ''
    def ir(f,w=1.3): col(); c.goto('about:blank',wait=.1); c.goto(B+f,wait=w)
    def cel(nome,coluna):   # valor de uma coluna (cabeçalho) na linha cujo Insumo é nome
        return J(f"""(()=>{{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); if(!t) return ''; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());
          const iI=hs.indexOf('INSUMO'), i=hs.indexOf({json.dumps(coluna.upper())}); const r=[...t.querySelectorAll('[role=row]')].find(x=>{{const cs=x.querySelectorAll('[role=cell]'); return cs[iI]&&cs[iI].innerText.replace(/\\s+/g,' ').trim()==={json.dumps(nome)};}});
          return r?[...r.querySelectorAll('[role=cell]')][i].innerText.replace(/\\s+/g,' ').trim():'(sem linha)';}})()""") or ''
    def rowclick(t):
        r=J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(t)})>=0); if(!r) return 'sem linha'; r.scrollIntoView({{block:'center'}}); (r.querySelector('[role=cell] b')||r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.5); return r
    def memo():
        ls=[x.strip() for x in (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').split('\n') if x.strip()]
        i=next((k for k,x in enumerate(ls) if x.startswith('Estoque apto hoje')),None); j=next((k for k,x in enumerate(ls) if x.startswith('Necessidade líquida =') or x.startswith('Sem falta nesta safra') or x.startswith('Sem compra nova')),None)
        return ls[i:j+1] if i is not None and j is not None else ls
    def fechar(): J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return; const b=[...a.querySelectorAll('button')].find(b=>/^Fechar$|^×$/.test(b.innerText.trim())||b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()"); time.sleep(.35)
    k6=lambda: J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]") or ''
    foto=lambda n: c.shot(os.path.join(OUT,f'q_ctl4_{n}.png'))
    pagw=lambda: J("[document.documentElement.scrollWidth, innerWidth]") or [0,0]
    def saf():
        ir('SAF.dc.html#saf=S2627&passo=demanda',w=1.6); clk('Expandir tudo',w=.6)
    def mapa(faz='Santa Rita',per='Safra toda',tsel=()):
        J(f"sessionStorage.setItem('mapa-ctx',{json.dumps(json.dumps({'mf_faz':faz,'lay':'Insumos','tsel':list(tsel),'flt':{'Insumos':{'per':per}}}))})"); ir('IN-04.dc.html',w=2.0)
        if faz=='Lagoa Grande':   # mapa real (MapLibre): espera os pivôs
            for _ in range(80):
                if J("!!(window.__LGI&&__LGI.pronto)"): break
                time.sleep(.25)
            time.sleep(.6)
    pan1=lambda: (J("(()=>{const a=document.querySelector('aside[aria-label]'); return a?a.innerText:'';})()") or '').replace('\n',' · ')
    SV="[...document.querySelectorAll('svg [role=button]')]"
    lab=lambda t: J(f"(()=>{{const e={SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); return e?e.getAttribute('aria-label'):'';}})()") or ''
    def tap(t): J(f"(()=>{{const e={SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); e&&e.dispatchEvent(new MouseEvent('click',{{bubbles:true}}));}})()"); time.sleep(.5)
    pan=lambda t: (J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{}}).innerText||''") or '').replace('\n',' · ')
    nums=lambda: (J("(document.querySelector('[role=group][aria-label^=\"Indicadores de\"]')||{innerText:''}).innerText") or '').replace('\n',' ')
    cen=lambda e: J(f"(()=>{{const c=window.__cen.cenGet(); return ({e});}})()")   # só na tela O.S. (expõe window.__cen)
    def os_painel(oid):
        ir('OS.dc.html',w=1.6)
        J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.trim().startsWith({json.dumps(oid)})); r&&r.click();}})()"); time.sleep(.6)
    def motivo(txt):
        J(f"(()=>{{const i=document.querySelector('textarea[aria-label=\"Motivo do cancelamento\"]'); if(!i) return; const P=HTMLTextAreaElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(txt)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.3)
    c.size(1440,1000); ir('SAF.dc.html'); J("localStorage.clear(); sessionStorage.clear()")
    # ================= normal (1440 px) =================
    saf(); t6=k6(); foto('1_saf_demanda')
    chk('N1 Planejar safra › etapa 4 (2026/27): R$ 430.255,00 · 14 insumos a comprar · SOL-2026-07 em cotação (a mesma conta da Compra)',
        t6.startswith('Valor da necessidade líquida R$ 430.255,00 · 14 insumos a comprar · solicitação SOL-2026-07'),t6)
    fa=[cel('Fungicida A',k) for k in ('Necessidade líquida','Situação')]; mp=[cel('MAP 11-52',k) for k in ('Necessidade líquida','Falta em')]
    ur=[cel('Ureia 45%',k) for k in ('Necessidade líquida','Falta em','Situação')]; hd=J("[...document.querySelectorAll('[role=columnheader]')].filter(h=>h.offsetParent).map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim())") or []
    chk('N2 compra em dobro desfeita: Fungicida A "0,0 L · Coberto pelo estoque" (nunca 145,2 L); compra a menos desfeita: MAP "80.000 kg" em 18/10/2026 e Ureia da OS-0418 "1.140 kg" em 24/09/2026 · coluna "Antes de hoje sem O.S." (nunca "Já realizado")',
        fa==['0,0 L','Coberto pelo estoque'] and mp==['80.000 kg','18/10/2026'] and ur==['1.140 kg','24/09/2026','Em cotação'] and 'ANTES DE HOJE SEM O.S.' in [h.upper() for h in hd] and 'JÁ REALIZADO' not in [h.upper() for h in hd],(fa,mp,ur,hd))
    rowclick('Fungicida A'); fs=memo(); fechar()
    chk('N3 memória do Fungicida A: a OS-0421 conta pelo pendente (15 L), a reserva da OS-0424 conta uma vez e o plano entra só na parte sem O.S.',
        '23/09/2026 · T1+T2 · OS-0421 · Fungicida 1ª aplicação · 0,50 L/ha × 160 ha − 65 L em custódia = 15,0 L → saldo 530 L' in fs
        and '24/09/2026 · Reserva REQ-039 · OS-0424 (T1-B) · 65,0 L da mesma demanda, contados uma vez' in fs
        and sum('OS-0421' in l for l in fs)==4 and fs[-1].startswith('Sem falta nesta safra'),fs)
    rowclick('MAP 11-52'); ms=memo(); fechar()
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.6); clk('Expandir tudo',w=.6); tot=J("[...document.querySelectorAll('.g2tot')].filter(x=>x.offsetParent).map(x=>x.innerText).join(' ')") or ''
    rowclick('MAP 11-52'); mc=memo(); fechar(); ur2=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Ureia 45%')>=0); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''; foto('2_cmp_etapa2')
    chk('N4 Compra › etapa 2 lê a mesma demanda: total R$ 430.255,00, Ureia 1.140 kg e a memória do MAP igual, linha a linha, à do Planejar safra (com a OS-0420 e a OS-0431)',
        '430.255,00' in tot and '1.140' in ur2 and mc==ms and any('OS-0420' in l for l in ms) and any('OS-0431' in l for l in ms),(tot,ur2,ms[:4],mc[:4]))
    mapa(); n0=nums(); f0=body(); tap('T4'); p4=pan('T4'); tap('T4'); tap('T1'); p1=pan('T1'); tap('T1'); foto('3_mapa_sr')
    chk('N5 Mapa › Insumos (Santa Rita, safra toda): 19 produtos · 14 faltam · 3 aguardando pedido · 2 estoque cobre; T4 "MAP 11-52 · 17.500 kg" com "Falta 80.000 kg"; T1 Fungicida A "Estoque cobre"; a fonte diz que é a necessidade líquida da Safra 2026/27, a mesma do Planejar safra e da Compra',
        all(x in n0 for x in ('Produtos no período 19','Faltam 14','Aguardando pedido 3','Estoque cobre 2')) and 'MAP 11-52 · 17.500 kg' in p4 and 'Falta 80.000 kg' in p4
        and 'Fungicida A' in p1 and 'Falta 145' not in p1 and 'Falta 130' not in p1
        and 'necessidade líquida da Safra 2026/27' in f0 and 'a mesma do Planejar safra e da Compra' in f0 and 'sem plano: O.S. abertas' not in f0,(n0,p4[:400],p1[:300]))
    mapa('Lagoa Grande',tsel=['PV13']); p13=pan1(); f13=body(); foto('4_mapa_lg')
    chk('N6 Mapa › Insumos (Lagoa Grande): PV13 Glifosato "Falta 293 L" — o estoque da Santa Rita não cobre outra fazenda',
        'Glifosato 480' in p13 and 'Falta 293 L' in p13 and 'necessidade líquida da Safra Mamão 2026/27' in f13,p13[:400])
    # ================= recusa =================
    os_painel('OS-0418'); a=clk('Cancelar sem execução','aside[role=dialog]'); b=clk('Confirmar cancelamento','aside[role=dialog]'); al=T(); e0=cen("c.ordens['OS-0418'].etapa")
    saf(); u0=cel('Ureia 45%','Necessidade líquida')
    chk('R1 recusa: cancelar a OS-0418 sem motivo é recusado ("Informe o motivo do cancelamento."), a ordem segue A liberar e a Ureia continua 1.140 kg na demanda',
        a=='ok' and b=='ok' and 'Informe o motivo do cancelamento' in al and e0=='A liberar' and u0=='1.140 kg',(a,b,al,e0,u0))
    # ================= a O.S. muda e a demanda acompanha (mesmo estado, sem redigitar) =================
    os_painel('OS-0418'); clk('Cancelar sem execução','aside[role=dialog]'); motivo('Fertirrigação adiada (teste CTL-4)'); clk('Confirmar cancelamento','aside[role=dialog]'); tc=T()
    saf(); t6b=k6(); u1=cel('Ureia 45%','Necessidade líquida'); foto('5_saf_os0418_cancelada')
    chk('I1 OS-0418 cancelada na tela O.S. → Planejar safra recalcula na hora: Ureia sai da demanda (0 kg; a linha fica só porque a SOL ainda a pede, U1); R$ 426.721,00 · 13 insumos a comprar',
        'OS-0418 cancelada sem execução' in tc and u1=='0 kg' and t6b.startswith('Valor da necessidade líquida R$ 426.721,00 · 13 insumos a comprar'),(tc,u1,t6b))
    mapa(); n1=nums(); tap('P1'); pp=pan('P1'); tap('P1')
    chk('I2 Mapa › Insumos acompanha: 18 produtos · 13 faltam; P1 sem Ureia',all(x in n1 for x in ('Produtos no período 18','Faltam 13')) and 'Ureia' not in pp,(n1,pp[:300]))
    # ================= a SOL já enviada pede mais do que a demanda de agora (a O.S. saiu depois do envio): o Planejar safra mostra e atualiza =================
    prim=lambda: (J("(()=>{const b=[...document.querySelectorAll('.acoes-prim')].find(x=>x.offsetParent); return b?b.innerText.replace(/\\s+/g,' ').trim():'';})()") or '')
    saf(); ux=[cel('Ureia 45%',k) for k in ('Necessidade líquida','Situação','Solicitação')]; t6x=k6(); px=prim(); rowclick('Ureia 45%'); mu=memo(); fechar(); foto('5b_saf_acima')
    chk('U1 a SOL-2026-07 ainda pede os 1.140 kg de Ureia da OS-0418 cancelada: a linha fica "0 kg · Acima da demanda · 1.140 kg · SOL-2026-07", a faixa conta "1 insumo acima da demanda" e a primária é "Atualizar SOL-2026-07" (nunca comprar a mais em silêncio)',
        ux==['0 kg','Acima da demanda · 1.140 kg','SOL-2026-07'] and '1 insumo acima da demanda' in t6x and px=='Atualizar SOL-2026-07'
        and any('SOL-2026-07 pede 1.140 kg' in l for l in mu),(ux,t6x,px,mu[:3]))
    clk('Atualizar SOL-2026-07',w=.8); tu1=T(); u3=cel('Ureia 45%','Necessidade líquida'); t6y=k6(); py=prim()
    chk('U2 atualizar: a SOL-2026-07 perde só a Ureia (toast com 1.140 kg e R$ 3.534,00), a linha some e a primária volta a "Abrir Compra de insumos ›"',
        'SOL-2026-07 atualizada' in tu1 and 'Ureia 45%' in tu1 and '1.140 kg' in tu1 and 'R$ 3.534,00' in tu1 and u3=='(sem linha)' and 'acima da demanda' not in t6y and py=='Abrir Compra de insumos ›',(tu1,u3,t6y,py))
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.6); clk('Expandir tudo',w=.6); tot2=J("[...document.querySelectorAll('.g2tot')].filter(x=>x.offsetParent).map(x=>x.innerText).join(' ')") or ''
    ur3=J("[...document.querySelectorAll('[role=row]')].some(r=>r.innerText.indexOf('Ureia 45%')>=0)"); foto('5c_cmp_sol_atualizada')
    chk('U3 a Compra lê a versão nova da SOL-2026-07: total R$ 426.721,00 (o mesmo do Planejar safra) e nenhuma linha de Ureia',
        '426.721,00' in tot2 and not ur3,(tot2,ur3))
    saf(); clk('Atualizar SOL-2026-07',w=.6); pz=prim()
    chk('U4 repetição: com a SOL já atualizada não há o que atualizar; a primária segue "Abrir Compra de insumos ›"',pz=='Abrir Compra de insumos ›',pz)
    # ================= repetição =================
    saf(); t6c=k6(); ir('SAF.dc.html#saf=S2627&passo=demanda',w=1.6); clk('Expandir tudo',w=.6); t6d=k6(); rowclick('Fungicida A'); fs2=memo(); fechar()
    chk('P1 repetição: recarregar duas vezes dá a mesma conta (R$ 426.721,00) e não duplica a ordem na memória (OS-0421 uma vez pelo pendente)',
        t6c==t6y and t6d==t6y and t6y.startswith('Valor da necessidade líquida R$ 426.721,00') and fs2==fs,(t6c,t6d,fs2[:3]))
    os_painel('OS-0418'); temc=J("[...document.querySelectorAll('aside[role=dialog] button')].some(b=>b.innerText.trim()==='Cancelar sem execução')")
    r2=J("(()=>{ const X=window.__cen; const r=X.cenMudar(null,c=>X.osc_cancelar(c,'OS-0418','de novo',['','',''],{k:'Ana'})); return r.erro||r.msg||''; })()") or ''
    saf(); t6e=k6()
    chk('P2 repetição: a OS-0418 cancelada não oferece cancelar de novo; o comando repetido é recusado e a demanda não muda',not temc and 'Só ordem sem realizado' in r2 and t6e==t6y,(temc,r2,t6e))
    os_painel('OS-0418'); J("window.__cen.cenReset()"); saf(); t6f=k6()
    chk('P3 restaurar a demonstração volta aos números da semente (R$ 430.255,00 · 14 insumos)',t6f.startswith('Valor da necessidade líquida R$ 430.255,00 · 14 insumos a comprar'),t6f)
    # ================= revisão do CTL-4, achado 1 (S2): estoque, reservas e recebimentos do MESMO cenário das O.S. =================
    J("localStorage.removeItem('talhao-os-compras-v1')"); mapa(); tap('C1'); c0=pan('C1'); tap('C1')
    from est_lib import FIND
    ir('EST.dc.html',w=1.6); J("document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[1].click()"); time.sleep(.5)
    re_=J(f"(()=>{{const r=({FIND})(['REQ-040','NPK 20-05-20']); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.5)
    clk('Salvar','aside[role=dialog]',w=.8); te=T()
    saf(); t6v=k6(); nv=[cel('NPK 20-05-20',k) for k in ('Necessidade líquida','Estoque apto','Situação')]; pv=prim(); foto('10_saf_entrega_npk')
    chk('V1 entrega comum no Estoque (8.000 kg de NPK da REQ-040 para a OS-0425) não muda a compra: NPK "14.800 kg", estoque apto "0 kg", sem "Acima da demanda"; R$ 430.255,00 e a primária segue "Abrir Compra de insumos ›" (na base: 6.800 kg e "Atualizar SOL-2026-07" cortava R$ 27.200)',
        re_=='ok' and 'entregues' in te and t6v==t6f and nv[0]=='14.800 kg' and nv[1]=='0 kg' and 'Acima' not in nv[2] and pv=='Abrir Compra de insumos ›',(re_,te,t6v,nv,pv))
    mapa(); tap('C1'); c1=pan('C1'); tap('C1')
    chk('V2 Mapa › Insumos depois da entrega: C1 continua "Falta 14.800 kg" (o mesmo de antes)','Falta 14.800 kg' in c0 and 'Falta 14.800 kg' in c1,(c0[:300],c1[:300]))
    # ================= achado 2 (S3): a Compra mostra a SOL acima da demanda de agora (sem trava) =================
    ir('OS.dc.html',w=1.6); rc=J("(()=>{ const X=window.__cen; const r=X.cenMudar(null,c=>X.osc_cancelar(c,'OS-0418','fertirrigação adiada (teste CTL-4)',['','',''],{k:'Ana'})); return r.erro||r.msg||''; })()") or ''
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.6); clk('Expandir tudo',w=.6); uc=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Ureia 45%')>=0); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
    k2c=J("(document.body.innerText.match(/SOL-2026-07 · [^\\n]*enviada em[^\\n]*/)||[''])[0]") or ''; foto('11_cmp_acima')
    chk('C1 Compra › etapa 2 com a OS-0418 cancelada: a Ureia mostra "Acima da demanda · 1.140 kg · o Planejar safra atualiza a SOL-2026-07" e a faixa conta "1 insumo acima da demanda de agora" (o NPK entregue não aparece)',
        'cancelada' in rc and 'Acima da demanda · 1.140 kg' in uc and 'o Planejar safra atualiza a SOL-2026-07' in uc and '1 insumo acima da demanda de agora' in k2c,(rc,uc,k2c))
    # ================= recusa na Compra (DEM-08): sem proposta a tempo, a padrão é a que chega primeiro; mais cara e mais tardia exige justificativa =================
    J("localStorage.removeItem('talhao-os-compras-v1')"); ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.6)
    from comp_lib import IR_ETAPA
    J(f"({IR_ETAPA})(3)"); time.sleep(.5); clk('Enviar convites (simulado)'); time.sleep(6.5); clk('Comparar propostas',w=.8); clk('Expandir tudo',w=.6)
    tu=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Ureia 45%')>=0); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
    rr=J("""(()=>{const rows=[...document.querySelectorAll('[role=row].g2ed')]; const i=rows.findIndex(r=>/Ureia 45%/.test(r.innerText)); const k=rows.slice(i+1).find(r=>/Coop\\. Vale/.test(r.innerText)); if(!k) return 'sem proposta'; k.querySelector('[role=cell] span').click(); return 'ok';})()"""); time.sleep(.5)
    clk('Salvar','aside[role=dialog]'); al2=J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')") or ''
    chk('R2 Compra › etapa 4 (DEM-08): Ureia sai em Casa do Adubo "Chega primeiro", sem justificativa pendente; escolher a Coop. Vale (mais cara e mais tardia) é recusado sem justificativa',
        'Casa do Adubo' in tu and 'Chega primeiro' in tu and 'Justificativa pendente' not in tu and rr=='ok' and 'Informe justificativa' in al2,(tu,rr,al2))
    clk('Cancelar','aside[role=dialog]'); clk('Descartar alterações','aside[role=dialog]'); foto('6_cmp_etapa4')
    J(f"({IR_ETAPA})(5)"); time.sleep(.6); clk('Expandir tudo',w=.6); u5=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent).find(r=>r.innerText.indexOf('Ureia 45%')>=0); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
    chk('C2 a mesma Ureia avisa na etapa 4 (comparação) e na 5 (aprovação): "Acima da demanda · 1.140 kg", sem trava',
        'Acima da demanda · 1.140 kg' in tu and 'Acima da demanda · 1.140 kg' in u5,(tu,u5))
    # ================= achado 3 (S3): quem atualiza a SOL — papel exigido e autor gravado =================
    rec=lambda: J("(()=>{try{const o=JSON.parse(localStorage.getItem('talhao-os-compras-v1')); const s=o&&o.sols&&o.sols.S2627; return s?{por:s.por||'',em:s.em||'',atu:s.atu||null,hist:(s.hist||[]).length,ureia:(s.itens||{})['Ureia 45%']||null}:null;}catch(e){return 'erro '+e.message}})()")
    J("localStorage.setItem('safrion.perfilDemo','Zé')"); saf(); pz0=prim(); r0=rec(); clk('Atualizar SOL-2026-07',w=.8); tz=T(); r1=rec()
    chk('Q1 o perfil Zé (mecânico) não atualiza a SOL: "Atualizar a SOL-2026-07: decisão de Ana (gestora). Nada foi alterado." e o registro não muda',
        pz0=='Atualizar SOL-2026-07' and 'decisão de Ana (gestora)' in tz and 'Nada foi alterado' in tz and r1==r0,(pz0,tz,r0,r1))
    J("localStorage.setItem('safrion.perfilDemo','Ana')"); saf(); clk('Atualizar SOL-2026-07',w=.8); ta=T(); r2=rec()
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.6); k2q=J("(document.body.innerText.match(/SOL-2026-07 · [^\\n]*enviada em[^\\n]*/)||[''])[0]") or ''
    chk('Q2 Ana (gestora) atualiza: o envio original fica (23/09/2026 10:40 por Ana (gestora)), a versão nova grava quem e quando ("Ureia 45% −1.140 kg"), o toast avisa que a cotação em andamento recomeça e a Compra mostra "atualizada em … por Ana (gestora)" sem aviso de acima da demanda',
        'Atualizada por Ana (gestora)' in ta and 'recomeça nesta versão' in ta and r2 and r2['por']=='Ana (gestora)' and r2['em']=='23/09/2026 10:40' and r2['atu'] and r2['atu']['por']=='Ana (gestora)'
        and r2['atu']['txt']=='Ureia 45% −1.140 kg' and r2['hist']==1 and r2['ureia'] is None and 'atualizada em 23/09/2026 ' in k2q and 'por Ana (gestora)' in k2q and 'acima da demanda' not in k2q,(ta,r2,k2q))
    # ================= risco lido 1 da revisão: pedido emitido antes de um complemento continua impedindo a redução (pedEmit na versão nova) =================
    J("localStorage.clear(); sessionStorage.clear()"); import dados2 as _D2
    _it={n:round(o['liq'],3) for n,o in _D2.demanda('S2627').items() if o['liq']>0.001}; _it['MAP 11-52']=62500
    _reg={'v':1,'sols':{'S2627':{'id':'SOL-2026-07','safra':'S2627','nome':'Safra 2026/27','faz':'Santa Rita','at':'23/09/2026','em':'23/09/2026 10:40','por':'Ana (gestora)','itens':_it,'comp':0,'estado':'Pedidos emitidos · PC-2026-101'}},
          'proc':{'S2627':{'sol':'SOL-2026-07','key':'x','comp':0,'estado':'Pedidos emitidos · PC-2026-101'}}}
    J(f"localStorage.setItem('talhao-os-compras-v1',{json.dumps(json.dumps(_reg,ensure_ascii=False))})"); saf(); pe0=prim(); mpc=cel('MAP 11-52','Situação')
    clk('Enviar para cotação',w=.8); tpc=T(); rpe=J("(()=>{const s=JSON.parse(localStorage.getItem('talhao-os-compras-v1')).sols.S2627; return {comp:s.comp,pedEmit:s.pedEmit,ureia:s.itens['Ureia 45%'],map:s.itens['MAP 11-52']};})()")
    ir('OS.dc.html',w=1.6); rc2=J("(()=>{ const X=window.__cen; const r=X.cenMudar(null,c=>X.osc_cancelar(c,'OS-0418','fertirrigação adiada (teste CTL-4, pedido emitido)',['','',''],{k:'Ana'})); return r.erro||r.msg||''; })()") or ''
    saf(); upe=cel('Ureia 45%','Situação'); ppe=prim(); rowclick('Ureia 45%'); mpe=(J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').split('\n'); fechar(); rpe2=J("JSON.parse(localStorage.getItem('talhao-os-compras-v1')).sols.S2627.itens['Ureia 45%']")
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.6); clk('Expandir tudo',w=.6); uce=J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Ureia 45%')>=0); return r?r.innerText.replace(/\\s+/g,' '):'';})()") or ''
    foto('12_saf_pedido_emitido')
    chk('P1 pedido emitido e depois complemento (MAP 62.500 → 80.000 kg): a versão nova guarda o pedido emitido; com a OS-0418 cancelada a Ureia fica "Acima da demanda · 1.140 kg" com "Pedido já emitido", a primária é "Abrir Compra de insumos ›" (não "Atualizar"), a SOL mantém os 1.140 kg e a Compra avisa "pedido já emitido: o excedente entra no estoque"',
        pe0=='Enviar para cotação' and 'Complemento' in mpc and 'Complemento SOL-2026-07-C1' in tpc and rpe=={'comp':1,'pedEmit':True,'ureia':1140,'map':80000} and 'cancelada' in rc2
        and upe=='Acima da demanda · 1.140 kg' and ppe=='Abrir Compra de insumos ›' and any('Pedido já emitido' in x for x in mpe) and rpe2==1140
        and 'Acima da demanda · 1.140 kg' in uce and 'pedido já emitido: o excedente entra no estoque' in uce,(pe0,mpc,tpc,rpe,rc2,upe,ppe,mpe[:3],rpe2,uce))
    # ================= plano mudado na tela: a Compra avisa pela conta da versão (ent), nunca pelo plano da semente =================
    J("localStorage.clear(); sessionStorage.clear()"); ir('SAF.dc.html#saf=S2627&passo=cultivos',w=1.6); ap1=clk('Aplicar plano em 4 cultivos',w=.6); ap2=clk('Aplicar plano','aside[role=dialog]',w=.8); tap_=T()
    J(f"({IR_ETAPA})(4)"); time.sleep(.6); clk('Expandir tudo',w=.6); t6p=k6(); ep=clk('Enviar para cotação',w=.8)
    if ep!='ok': ep=clk('Atualizar SOL-2026-07',w=.8)
    tep=T()
    rent=J("(()=>{const s=JSON.parse(localStorage.getItem('talhao-os-compras-v1')).sols.S2627; return {comp:s.comp,occ:((s.ent||{}).occ||[]).length,n:Object.keys(s.itens).length};})()")
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.6); k2p=J("(document.body.innerText.match(/SOL-2026-07 · [^\\n]*enviada em[^\\n]*/)||[''])[0]") or ''; foto('13_cmp_plano_tela')
    chk('A1 "Aplicar plano em 4 cultivos" na tela e complemento enviado: a versão da SOL guarda o plano da conta e a Compra não avisa "acima da demanda" (com o plano da semente avisaria os insumos do complemento à toa)',
        ap1=='ok' and ap2=='ok' and 'Complemento SOL-2026-07-C1' in tep and rent['comp']==1 and rent['occ']>0 and 'enviada em' in k2p and 'acima da demanda' not in k2p,(ap1,ap2,tap_,t6p,tep,rent,k2p))
    J("localStorage.clear(); sessionStorage.clear()")
    # ================= 390 px =================
    c.size(390,844); saf(); w1=pagw(); t390=k6(); u390=cel('Ureia 45%','Necessidade líquida'); rowclick('MAP 11-52'); m390=memo(); fechar(); foto('7_saf_390')
    chk('M1 390 px · Planejar safra etapa 4: a página não rola na horizontal; mesma conta (R$ 430.255,00 · 14 insumos), Ureia 1.140 kg e a memória do MAP igual à do desktop',
        w1[0]<=w1[1]+1 and t390.startswith('Valor da necessidade líquida R$ 430.255,00 · 14 insumos a comprar') and u390=='1.140 kg' and m390==ms,(w1,t390,u390,m390[:3]))
    mapa(); w2=pagw(); n390=nums(); tap('T4'); p390=pan('T4'); foto('8_mapa_390')
    chk('M2 390 px · Mapa › Insumos: sem rolagem horizontal; T4 "MAP 11-52 · 17.500 kg" e "Falta 80.000 kg"',w2[0]<=w2[1]+1 and 'MAP 11-52 · 17.500 kg' in p390 and 'Falta 80.000 kg' in p390,(w2,n390,p390[:300]))
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.6); w3=pagw(); b3=body(); foto('9_cmp_390')
    chk('M3 390 px · Compra etapa 2: sem rolagem horizontal da página e o mesmo total R$ 430.255,00',w3[0]<=w3[1]+1 and '430.255,00' in b3,(w3,))
    col(); chk('E1 sem erro JS nas telas abertas (Planejar safra, Compra, Mapa, O.S.)',ERR==[],ERR[:5])
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)
