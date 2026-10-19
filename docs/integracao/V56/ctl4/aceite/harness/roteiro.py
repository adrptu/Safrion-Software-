# -*- coding: utf-8 -*-
"""Contraprova (somente leitura) do S2 do Codex (comentário 6133690044, PR #47): devolução da REQ-031 + NF 4533 em quarentena
pela tela do Estoque, depois leitura da demanda no Planejar safra (SAF) e na Compra (CMP). Perfil novo do Chrome, storage limpo,
sem restaurar estado. Uso: python3 roteiro.py <sha7>"""
import sys, os, time, subprocess, json
SHA=sys.argv[1]; D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G=os.environ['GEN']; sys.path.insert(0,G)   # integração V56 × CTL-4: a pasta gen37 da candidata (o roteiro da contraprova, sem outra mudança)
from cdp import Chrome
from journeys import free
R=os.path.join(G,'_render'); LOGD=f'{D}/logs/{SHA}'; SHOT=f'{D}/shots/{SHA}'
os.makedirs(LOGD,exist_ok=True); os.makedirs(SHOT,exist_ok=True)
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js; B=f'http://127.0.0.1:{p}/'
c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__err=[];addEventListener('error',e=>window.__err.push(String(e.message)));"})
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
FIND="""((ts)=>[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent).find(r=>ts.every(t=>r.innerText.indexOf(t)>=0)))"""
# linha como {CABEÇALHO: texto da célula}; a linha é a que tem uma célula começando pelo nome (grade visível)
ROWD="""((nome)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const out=[];
  [...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).forEach(t=>{
    const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>n(h.innerText.replace(/[⇅▾▴▼▲]/g,'')).replace(/ · \\d+$/,''));
    [...t.querySelectorAll('[role=row]')].forEach(r=>{ const cs=[...r.querySelectorAll('[role=cell]')]; if(!cs.length) return;
      if(!cs.some(cx=>n(cx.innerText).startsWith(nome))) return; const o={}; cs.forEach((cx,i)=>{ o[hs[i]||('col'+i)]=n(cx.innerText); }); out.push(o); }); });
  return out;})"""
LOG=[]; V={'sha':SHA,'leituras':{}}
def log(*a):
    s=' '.join(a if all(isinstance(x,str) for x in a) else [x if isinstance(x,str) else json.dumps(x,ensure_ascii=False) for x in a]); LOG.append(s); print(s,flush=True)
ITENS=['MAP 11-52','Semente de soja 58 W']
try:
    clk=lambda t,root=None,w=.45: (J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"),time.sleep(w))[0]
    setv=lambda sel,v: (J(f"({SETV})({json.dumps(sel)},{json.dumps(v)})"),time.sleep(.25))[0]
    T=lambda: J("[...document.querySelectorAll('[role=status],[role=alert]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def ir(f,w=1.6): c.goto('about:blank',wait=.1); c.goto(B+f,wait=w)
    rowd=lambda nome: J(f"({ROWD})({json.dumps(nome)})") or []
    prim=lambda: J("(()=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const a=[...document.querySelectorAll('.acoes-prim')].filter(x=>x.offsetParent).map(x=>n(x.innerText)); const g=[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>n(b.innerText)); return {acoes_prim:a,botao_verde:g};})()")
    klines=lambda: J("(()=>{const t=(document.querySelector('main')||document.body).innerText.split('\\n').map(l=>l.trim()).filter(Boolean); return t.filter(l=>/Valor da necessidade|necessidade|quarentena|Coberto|SOL-2026-07/i.test(l)).slice(0,14);})()")
    g2tot=lambda: J("[...document.querySelectorAll('.g2tot')].filter(x=>x.offsetParent).map(x=>x.innerText.replace(/\\s+/g,' ').trim())")
    totrow=lambda: J("(()=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); if(!t) return ''; const rs=[...t.querySelectorAll('[role=row]')].filter(r=>/^total/i.test(n(r.innerText))); return rs.map(r=>n(r.innerText));})()")
    def memo(nome):
        J(f"(()=>{{const r=({FIND})([{json.dumps(nome)}]); if(!r) return; r.scrollIntoView({{block:'center'}}); (r.querySelector('[role=cell] b')||r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.7)
        t=(J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').split('\n'); t=[x.strip() for x in t if x.strip()]
        clk('Fechar','aside[role=dialog]',w=.4); J("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.3)
        return t[:40]
    foto=lambda n: c.shot(os.path.join(SHOT,f'{n}.png'))
    def foto_linhas(tag,tela):
        # captura focada: cada linha (MAP, Semente) no centro e a grade rolada até a coluna ESTOQUE APTO
        for n,suf in (('MAP 11-52','MAP'),('Semente de soja 58 W','SEMENTE')):
            J(f"""(()=>{{const r=({FIND})([{json.dumps(n)}]); if(!r) return; r.scrollIntoView({{block:'center'}});
              const h=[...document.querySelectorAll('[role=columnheader]')].filter(x=>x.offsetParent).find(x=>/ESTOQUE APTO/i.test(x.innerText)); if(h) h.scrollIntoView({{block:'nearest',inline:'center'}});}})()"""); time.sleep(.5)
            foto(f'{tag}_{tela}_{suf}')
    def ler_saf(tag):
        ir('SAF.dc.html#saf=S2627&passo=demanda',w=1.8); ex=clk('Expandir tudo',w=.7)
        o=dict(url='SAF.dc.html#saf=S2627&passo=demanda',expandir=ex,linhas={n:rowd(n) for n in ITENS},total_k=klines(),g2tot=g2tot(),linha_total=totrow(),primaria=prim())
        foto(f'{tag}_SAF'); foto_linhas(tag,'SAF'); o['memoria']={n:memo(n) for n in ITENS}; return o
    def ler_cmp(tag):
        ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.8)
        ex=J("[...document.querySelectorAll('button')].some(b=>b.offsetParent&&b.innerText.trim()==='Recolher tudo')") and 'já expandida (Recolher tudo visível)' or clk('Expandir tudo',w=.7)
        o=dict(url='CMP.dc.html#sol=SOL-2026-07&saf=S2627',expandir=ex,linhas={n:rowd(n) for n in ITENS},total_k=klines(),g2tot=g2tot(),linha_total=totrow(),primaria=prim())
        foto(f'{tag}_CMP'); foto_linhas(tag,'CMP'); o['memoria']={n:memo(n) for n in ITENS}; return o
    def est_secao(i): ir('EST.dc.html',w=1.7); r=J(f"(()=>{{const b=document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[{i-1}]; if(!b) return 'sem seção'; b.click(); return b.innerText.replace(/\\s+/g,' ').trim();}})()"); time.sleep(.6); return r
    def cen_est():
        return J("""(()=>{const X=window.__cen; if(!X) return 'sem __cen'; const c=X.cenGet(); const L=c.lotes||{}; const pick=k=>L[k]?{fisico:L[k].fisico,quarentena:L[k].quarentena,reservado:L[k].reservado,validade:L[k].validade,local:L[k].local}:null;
          const r=(c.reqs||{})['REQ-031']; return {rev:c.rev,v:c.v,lote_M26_07:pick('MAP 11-52|M26-07'),lote_S58_0926:pick('Semente de soja 58 W|S58-0926'),
            lotes_semente:Object.keys(L).filter(k=>k.indexOf('Semente de soja 58 W|')===0).map(k=>[k,pick(k)]),lotes_map:Object.keys(L).filter(k=>k.indexOf('MAP 11-52|')===0).map(k=>[k,pick(k)]),
            req031:r?{estado:r.estado,itens:r.itens.map(i=>({prod:i.prod,lote:i.lote,solicitado:i.solicitado,entregue:i.entregue,consumido:i.consumido,devolvido:i.devolvido,custodia:i.custodia}))}:null,
            movs:(c.movs||[]).map(m=>({tipo:m.tipo,item:m.item||m.prod,lote:m.lote,q:m.q!==undefined?m.q:m.qtd,ref:m.ref||m.doc||''}))};})()""")
    def est_saldos():
        s=est_secao(4); J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&b.innerText.trim()==='Expandir tudo'); b&&b.click();})()"); time.sleep(.6)
        o=dict(secao=s,linhas={n:rowd(n) for n in ITENS},lotes={l:J(f"(()=>{{const r=({FIND})([{json.dumps(l)}]); return r?r.innerText.replace(/\\s+/g,' ').trim():'sem linha';}})()") for l in ('M26-07','S58-0926')},
               k=J("(document.querySelector('main').innerText.split('\\n').filter(l=>/·/.test(l)).slice(0,4))")); return o
    c.size(1440,1000); ir('SAF.dc.html'); J("localStorage.clear(); sessionStorage.clear()")
    log('storage após limpar:',J("({ls:localStorage.length,ss:sessionStorage.length})"))
    # ===== ANTES =====
    V['leituras']['0_antes']=dict(SAF=ler_saf('0_antes'),CMP=ler_cmp('0_antes'))
    est_secao(1); V['leituras']['0_antes']['EST_cenario']=cen_est(); V['leituras']['0_antes']['EST_saldos']=est_saldos(); foto('0_antes_EST_saldos')
    log('ANTES:',V['leituras']['0_antes'])
    # ===== PASSO 1 · Receba devoluções → REQ-031 → 500 kg → Salvar =====
    P1={}; P1['secao']=est_secao(3); P1['linha']=J(f"(()=>{{const r=({FIND})(['REQ-031','MAP 11-52']); if(!r) return 'sem linha'; const t=r.innerText.replace(/\\s+/g,' ').trim(); (r.querySelector('[role=cell] span')||r).click(); return t;}})()"); time.sleep(.6)
    P1['form_antes']=J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")[:900]
    P1['cond_padrao']=J("(document.querySelector('#fx_g_dev_cond')||{value:null}).value")
    P1['set_qtd']=setv('#fx_g_dev_qtd','500'); foto('1_form_devolucao')
    P1['salvar']=clk('Salvar','aside[role=dialog]',w=1.0); P1['recibo']=T(); foto('1_recibo_devolucao')
    P1['form_aberto_depois']=J("!!document.querySelector('aside[role=dialog]')")
    P1['cenario']=cen_est(); V['passo1']=P1; log('PASSO 1:',P1)
    V['leituras']['1_apos_devolucao']=dict(SAF=ler_saf('1_apos_dev'),CMP=ler_cmp('1_apos_dev'))
    V['leituras']['1_apos_devolucao']['EST_saldos']=est_saldos(); foto('1_apos_dev_EST_saldos')
    log('APÓS PASSO 1:',V['leituras']['1_apos_devolucao'])
    # ===== PASSO 2 · Confira recebimentos → NF 4533: conferida 20.000, apta 0, quarentena 20.000, motivo, validade 03/2027 → Salvar =====
    P2={}; P2['secao']=est_secao(1); P2['abrir']=clk('Conferir NF 4533',w=.8)
    P2['form_antes']=J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")[:1200]
    P2['sets']={k:setv(k,v) for k,v in (('#fx_g_rec_conf','20000'),('#fx_g_rec_apto','0'),('#fx_g_rec_quar','20000'),('#fx_g_rec_val','03/2027'),('#fx_g_rec_obs','Aguarda laudo de germinação (contraprova sintética)'))}
    P2['valores_form']=J("(()=>{const o={}; ['fx_g_rec_ped','fx_g_rec_nf','fx_g_rec_qtd_nf','fx_g_rec_conf','fx_g_rec_apto','fx_g_rec_quar','fx_g_rec_lote','fx_g_rec_val','fx_g_rec_local','fx_g_rec_div','fx_g_rec_obs'].forEach(k=>{const i=document.getElementById(k); o[k]=i?i.value:null;}); return o;})()")
    foto('2_form_recebimento')
    P2['salvar']=clk('Salvar','aside[role=dialog]',w=1.0); P2['recibo']=T(); P2['form_aberto_depois']=J("!!document.querySelector('aside[role=dialog]')"); foto('2_recibo_recebimento')
    P2['linha_NF4533']=J(f"(()=>{{const r=({FIND})(['NF 4533']); return r?r.innerText.replace(/\\s+/g,' ').trim():'sem linha';}})()")
    P2['cenario']=cen_est(); V['passo2']=P2; log('PASSO 2:',P2)
    V['leituras']['2_apos_quarentena']=dict(EST_saldos=est_saldos()); foto('2_apos_quar_EST_saldos')
    # ===== PASSO 3 · SAF (demanda, expandir) e CMP =====
    V['leituras']['3_final']=dict(SAF=ler_saf('3_final'),CMP=ler_cmp('3_final'))
    ir('EST.dc.html',w=1.6); V['leituras']['3_final']['EST_cenario']=cen_est()
    log('FINAL:',V['leituras']['3_final'])
    V['erros_js']=J("window.__err||[]"); log('erros JS:',V['erros_js'])
finally:
    try: c.close()
    finally: srv.terminate()
    json.dump(V,open(os.path.join(LOGD,'valores.json'),'w'),ensure_ascii=False,indent=1)
    open(os.path.join(LOGD,'roteiro.log'),'w').write('\n'.join(LOG))
