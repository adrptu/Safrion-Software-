# -*- coding: utf-8 -*-
"""Teste CDP · CTL-4, revisão do 16fb55e (PR #47, comentário 6136083713 do Codex): o laudo da quarentena no Estoque, pela tela.
Cada caso repete o contraexemplo do Codex com os comandos das próprias telas e falha no 16fb55e.
  L1 · ajuste 3 · o motivo é do lote aberto: abrir o laudo do K26-11, digitar "Motivo exclusivo K26-11", Manter bloqueado e abrir o F26-02 → o campo
       vem vazio (no 16fb55e: já trazia o motivo do KCl); trocar de lote direto pela linha também limpa; a abertura foca o nº do laudo e o Tab chega
       ao motivo; a 390×844 o painel e os controles cabem sem rolagem horizontal
  L2 · ajustes 2 e 4 · Ana devolve 10 L de Fungicida A bloqueados (REQ-035/F26-02), reprova LAB-A (motivo A), devolve mais 10 L e reprova LAB-B
       (motivo B): cada reprovação fica "revisão posterior pendente" como a liberação do mesmo acúmulo; a memória do Planejar safra diz 10 L/LAB-A e
       10 L/LAB-B, total 20, e o lote no Estoque mostra os dois laudos (no 16fb55e: "20 L · laudo LAB-B: motivo B" e reprovação sem marca)
  L3 · ajuste 4 (negativo) · Paula devolve bloqueado e Ana reprova: sem marca de revisão
  M1 · ajuste 1 · 30 L de Fungicida A devolvidos bloqueados e reprovados (LAB-9), e mais 10 L devolvidos bloqueados: 5,5 L de compra firme e 10 L
       aguardando laudo aparecem juntos no Planejar safra, na Compra, no Mapa, no SU-03det e no MB-05, sem somar à compra nem trocar a primária
       (no 16fb55e: Mapa, SU-03det e MB-05 só a falta). Estava no demanda_estado_nav_test, que com ele passou de 900 s sob carga (rc=124).
Uso: python3 est_laudo_lote_nav_test.py   (depois do build e do montar_render; capturas q_ctl4l_*.png em _probe/)"""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
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
GRP='[role=group][aria-label="Liberar quarentena com laudo"]'
try:
    clk=lambda t,root=None,w=.45: (J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"),time.sleep(w))[0]
    setv=lambda sel,v: (J(f"({SETV})({json.dumps(sel)},{json.dumps(v)})"),time.sleep(.25))[0]
    T=lambda: J("[...document.querySelectorAll('[role=status],[role=alert]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    val=lambda sel: J(f"(document.querySelector({json.dumps(sel)})||{{value:'(sem campo)'}}).value")
    foco=lambda: J("(document.activeElement||{}).id||''") or ''
    def ir(f,w=1.4): col(); c.goto('about:blank',wait=.1); c.goto(B+f,wait=w)
    foto=lambda n: c.shot(os.path.join(OUT,f'q_ctl4l_{n}.png'))
    def est_secao(i): ir('EST.dc.html',w=1.6); J(f"document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[{i-1}].click()"); time.sleep(.5)
    def est_row(*ts):
        r=J(f"(()=>{{const r=({FIND})({json.dumps(list(ts))}); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.5); return r
    def abrir_laudo(lote):   # "Liberar após inspeção" na linha do lote (Confira saldos), sem recarregar a página
        r=J(f"(()=>{{const r=({FIND})([{json.dumps(lote)}]); if(!r) return 'sem linha'; const b=[...r.querySelectorAll('button')].find(b=>/Liberar após inspeção/.test(b.innerText)); if(!b) return 'sem botão'; b.click(); return 'ok';}})()"); time.sleep(.6); return r
    def devolver(q,obs):
        est_secao(3); e=est_row('REQ-035','Fungicida A'); setv('#fx_g_dev_qtd',str(q)); setv('#fx_g_dev_cond','Bloqueada para inspeção · vai para quarentena'); setv('#fx_g_dev_obs',obs)
        clk('Salvar','aside[role=dialog]',w=.8); return e,T()
    def reprovar(lote,laudo,mot):
        est_secao(4); a=abrir_laudo(lote); m0=val('#est-laudo-mot'); setv('#est-laudo',laudo); setv('#est-laudo-mot',mot); r=clk('Reprovar com o laudo',GRP,w=.8); return a,m0,r,T()
    def perfil(k): J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(k)})")
    def memo(nome):
        ir('SAF.dc.html#saf=S2627&passo=demanda',w=1.7); clk('Expandir tudo',w=.6)
        J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(nome)})>=0); if(!r) return; r.scrollIntoView({{block:'center'}}); (r.querySelector('[role=cell] b')||r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.6)
        t=(J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').split('\n'); return [x.strip() for x in t if x.strip()]
    def cel(nome,coluna):   # valor de uma coluna (cabeçalho) na linha cujo Insumo é nome
        return J(f"""(()=>{{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); if(!t) return ''; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());
          const iI=hs.indexOf('INSUMO'), i=hs.indexOf({json.dumps(coluna.upper())}); const r=[...t.querySelectorAll('[role=row]')].find(x=>{{const cs=x.querySelectorAll('[role=cell]'); return cs[iI]&&cs[iI].innerText.replace(/\\s+/g,' ').trim()==={json.dumps(nome)};}});
          return r?[...r.querySelectorAll('[role=cell]')][i].innerText.replace(/\\s+/g,' ').trim():'(sem linha)';}})()""") or ''
    k6=lambda: J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]") or ''
    prim=lambda: (J("(()=>{const b=[...document.querySelectorAll('.acoes-prim')].find(x=>x.offsetParent); return b?b.innerText.replace(/\\s+/g,' ').trim():'';})()") or '')
    def safler(nomes,s='S2627'):
        ir(f'SAF.dc.html#saf={s}&passo=demanda',w=1.7); clk('Expandir tudo',w=.6)
        return dict(total=k6(),prim=prim(),**{n:[cel(n,k) for k in ('Necessidade líquida','Estoque apto','Situação')] for n in nomes})
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
    def su03det(): ir('SU-03det.dc.html',w=1.6); return (J("document.body.innerText") or '').replace('\n',' · ')
    def mb05(): ir('MB-05.dc.html',w=1.6); clk('Almoxarife',w=.6); return (J("document.body.innerText") or '').replace('\n',' · ')
    def tab(): c.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Tab','code':'Tab','windowsVirtualKeyCode':9}); c.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Tab','code':'Tab','windowsVirtualKeyCode':9}); time.sleep(.15)
    CABE="""(()=>{const g=document.querySelector('%s'); if(!g) return {sem:true}; const W=window.innerWidth; const els=[g].concat([...g.querySelectorAll('input,button')]).filter(e=>e.offsetParent!==null);
      const fora=els.filter(e=>{const b=e.getBoundingClientRect(); return b.left<-0.5||b.right>W+0.5;}).map(e=>(e.id||e.innerText||e.tagName).slice(0,30));
      return {W, sw:document.documentElement.scrollWidth, bsw:document.body.scrollWidth, fora, n:els.length};})()""" % GRP
    c.size(1440,1000); ir('EST.dc.html'); J("localStorage.clear(); sessionStorage.clear()"); perfil('Ana')
    # ================= L1 · ajuste 3: motivo por lote =================
    e0,t0=devolver(10,'Galão sem lacre (teste ajuste 3)')
    est_secao(4); a1=abrir_laudo('K26-11'); f1=foco(); setv('#est-laudo-mot','Motivo exclusivo K26-11'); mk=val('#est-laudo-mot')
    m1=clk('Manter bloqueado',GRP,w=.5); a2=abrir_laudo('F26-02'); f2=foco(); v2=val('#est-laudo-mot'); foto('l1_f26_depois_k26')
    setv('#est-laudo-mot','Motivo exclusivo F26-02'); a3=abrir_laudo('K26-11'); v3=val('#est-laudo-mot')   # troca direta pela linha, sem "Manter"
    setv('#est-laudo-mot','Motivo exclusivo K26-11'); a4=abrir_laudo('F26-02'); v4=val('#est-laudo-mot')
    J("document.getElementById('est-laudo')&&document.getElementById('est-laudo').focus()"); tab(); f5=foco()
    chk('L1 motivo é do lote aberto (ajuste 3, contraexemplo do Codex): K26-11 com "Motivo exclusivo K26-11", Manter bloqueado, abrir F26-02 → o motivo vem vazio; trocar de lote direto pela linha também limpa (F26-02 → K26-11 → F26-02); a abertura foca o nº do laudo e o Tab chega ao motivo (no 16fb55e: o F26-02 já trazia o motivo do KCl)',
        'devolvidos e bloqueados' in t0 and a1=='ok' and mk=='Motivo exclusivo K26-11' and m1=='ok' and a2=='ok' and v2=='' and a3=='ok' and v3=='' and a4=='ok' and v4==''
        and f1=='est-laudo' and f2=='est-laudo' and f5=='est-laudo-mot',dict(t0=t0[-80:],a=(a1,a2,a3,a4),m1=m1,mk=mk,v2=v2,v3=v3,v4=v4,foco=(f1,f2,f5)))
    c.size(390,844); est_secao(4); a6=abrir_laudo('F26-02'); time.sleep(.3); J(f"document.querySelector('{GRP}')&&document.querySelector('{GRP}').scrollIntoView({{block:'center'}})"); time.sleep(.3)
    cb=J(CABE) or {}; v6=val('#est-laudo-mot'); foto('l1_390_painel')
    chk('L1b a 390×844 o painel do laudo e os controles (nº do laudo, motivo, Liberar, Reprovar, Manter) cabem sem rolagem horizontal, e o motivo continua vazio',
        a6=='ok' and not cb.get('sem') and cb.get('fora')==[] and cb.get('sw',9999)<=cb.get('W',0) and cb.get('n',0)>=5 and v6=='',dict(a6=a6,cb=cb,v6=v6))
    J(f"(()=>{{const g=document.querySelector('{GRP}'); const b=g&&[...g.querySelectorAll('button')].find(b=>/Manter bloqueado/.test(b.innerText)); b&&b.click();}})()"); time.sleep(.4)
    c.size(1440,1000)
    # ================= L2 · ajustes 2 e 4: os comandos do item 2 pela tela (Ana devolve e reprova) =================
    ra,rm0,rr,ta=reprovar('F26-02','LAB-A','motivo A'); foto('l2_reprovado_lab_a')
    e2,tb=devolver(10,'Segundo galão sem lacre (teste ajuste 2)')
    rb,rm1,rr2,tb2=reprovar('F26-02','LAB-B','motivo B')
    est_secao(4); lote=(J(f"(()=>{{const r=({FIND})(['F26-02']); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''); foto('l2_lote_dois_laudos')
    mm=memo('Fungicida A'); foto('l2_memoria_por_laudo'); rep=[x for x in mm if x.startswith('Reprovado')]
    rv='revisão posterior pendente (Ana registrou a entrada bloqueada e decidiu)'
    chk('L2 memória por laudo (ajuste 2): depois de devolver 10 L, reprovar LAB-A (motivo A), devolver mais 10 L e reprovar LAB-B (motivo B), a memória do Planejar safra diz "Reprovado: 20 L do lote F26-02 (devolução da REQ-035) = 10 L no laudo LAB-A: motivo A + 10 L no laudo LAB-B: motivo B" e o lote no Estoque mostra "laudos LAB-A 10 L + LAB-B 10 L" (no 16fb55e: "20 L … laudo LAB-B: motivo B")',
        ra=='ok' and rr=='ok' and rb=='ok' and rr2=='ok' and rm0=='' and rm1=='' and 'reprovados com o laudo LAB-A' in ta and 'reprovados com o laudo LAB-B' in tb2
        and len(rep)==1 and rep[0].startswith('Reprovado: 20 L do lote F26-02 (devolução da REQ-035) = 10 L no laudo LAB-A: motivo A + 10 L no laudo LAB-B: motivo B')
        and 'Reprovado · 20 L · laudos LAB-A 10 L + LAB-B 10 L' in lote,dict(ta=ta[-160:],tb2=tb2[-160:],rep=rep,lote=lote[:300],rm=(rm0,rm1)))
    chk('L2b revisão posterior na reprovação (ajuste 4): Ana registrou as duas devoluções bloqueadas e reprovou — o aviso das duas reprovações diz "Fica '+rv+'" (a mesma regra da liberação), e a decisão vale',
        ('Fica '+rv) in ta and ('Fica '+rv) in tb2,dict(ta=ta[-220:],tb2=tb2[-220:]))
    # ================= L3 · ajuste 4 (negativo): pessoas distintas =================
    ir('EST.dc.html'); J("localStorage.clear(); sessionStorage.clear()"); perfil('Paula')
    e3,tc=devolver(10,'Galão sem lacre (teste ajuste 4, Paula)'); perfil('Ana')
    rc,rm2,rr3,td=reprovar('F26-02','LAB-N','motivo N')
    chk('L3 pessoas distintas (ajuste 4, negativo): Paula devolve bloqueado e Ana reprova com o laudo — a reprovação vale e não fica marca de revisão posterior',
        'devolvidos e bloqueados' in tc and rc=='ok' and rr3=='ok' and 'reprovados com o laudo LAB-N' in td and 'revisão posterior' not in td,dict(tc=tc[-120:],td=td[-220:],rc=rc))
    # ================= M1 · ajuste 1: falta firme + qualidade pendente juntas, nas cinco telas =================
    ir('EST.dc.html'); J("localStorage.clear(); sessionStorage.clear()"); perfil('Ana')
    e4,t4=devolver(30,'Galão sem lacre (teste ajuste 1)'); r9=reprovar('F26-02','LAB-9','lacre violado'); s2=safler(['Fungicida A'])
    e5,tm=devolver(10,'Galão amassado (teste ajuste 1)')
    s3=safler(['Fungicida A']); foto('m1_saf_falta_e_qualidade'); cm1=cmp_ler('Fungicida A'); mp=mapa('T2'); foto('m1_mapa_falta_e_qualidade'); su3=su03det(); foto('m1_su03det_falta_e_qualidade'); mb3=mb05(); foto('m1_mb05_falta_e_qualidade')
    chk('M1 falta firme + qualidade pendente (ajuste 1, S3): 30 L reprovados e mais 10 L devolvidos bloqueados — 5,5 L de compra firme e 10 L aguardando laudo nas cinco telas: Planejar safra "5,5 L" Complemento + "Qualidade pendente · 10,0 L" (primária e total iguais); Compra "Qualidade pendente · 10"; Mapa T2 "Falta 5 L" + "Qualidade pendente · 10 L" com motivo (o da devolução) e "o gestor libera ou reprova com o laudo no Estoque"; SU-03det "Pendência de compra · 5,5 L" + "Qualidade pendente · 10,0 L"; MB-05 "Conflito de reserva" + "Qualidade pendente · 10,0 L" (no 16fb55e: Mapa, SU-03det e MB-05 só a falta)',
        'devolvidos e bloqueados' in t4 and r9[2]=='ok' and 'reprovados com o laudo LAB-9' in r9[3] and 'Complemento' in s2['Fungicida A'][2] and 'devolvidos e bloqueados' in tm
        and s3['Fungicida A'][0]=='5,5 L' and 'Complemento' in s3['Fungicida A'][2] and 'Qualidade pendente · 10,0 L' in s3['Fungicida A'][2] and s3['prim']==s2['prim'] and s3['total'].startswith(s2['total'])
        and 'Qualidade pendente · 10' in cm1['row'] and 'Fungicida A' in mp and 'Falta 5 L' in mp and 'Qualidade pendente · 10 L' in mp and 'se o laudo reprovar, faltam mais 10 L · motivo: 10 L em quarentena aguardam laudo (lote F26-02 · devolução da REQ-035: Galão amassado (teste ajuste 1))' in mp
        and 'responsável: o gestor libera ou reprova com o laudo no Estoque' in mp
        and 'Pendência de compra · 5,5 L' in su3 and 'Qualidade pendente · 10,0 L' in su3 and 'Enviar o complemento no Planejar safra' in su3
        and 'Conflito de reserva' in mb3 and 'Qualidade pendente · 10,0 L' in mb3 and 'dependem do laudo da quarentena' in mb3 and 'Registrar divergência' in mb3,
        dict(t4=t4[-60:],r9=r9[3][-80:],s2=s2,s3=s3,cmp='Qualidade pendente · 10' in cm1['row'],mapa=[x for x in mp.split(' · ') if 'Fungicida' in x or 'Falta' in x or 'Qualidade' in x or 'quarentena' in x][:6],
             su=['Pendência de compra · 5,5 L' in su3,'Qualidade pendente · 10,0 L' in su3,'Enviar o complemento no Planejar safra' in su3],mb=['Conflito de reserva' in mb3,'Qualidade pendente · 10,0 L' in mb3,'dependem do laudo da quarentena' in mb3]))
    col(); chk('E1 sem erro JS nas telas abertas (Estoque, Planejar safra, Compra, Mapa, SU-03det, MB-05)',ERR==[],ERR[:5])
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)
