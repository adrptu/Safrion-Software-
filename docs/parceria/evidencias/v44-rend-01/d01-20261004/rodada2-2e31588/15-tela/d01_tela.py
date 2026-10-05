# -*- coding: utf-8 -*-
"""Sonda de tela do D-01 (5983640246) no Planejar safra, Controle de ácaro (T7, 42 ha), pelo formulário como o usuário faz:
A (fazenda, 6 m), B (prestador 12 m) e C (prestador 6 m) em sequência declarada com janela de 3 h e D (prestador 6 m) com 100 h.
Antes do D-01 a sequência dividia a maior janela (100 h): A+B+C = 7 h numa janela de 3 h, sem conflito. Com o D-01, A+B+C cabem em 3 h e o
conflito fica à vista. Controle positivo: as quatro "ao mesmo tempo, com recursos próprios": nenhuma restrição, 42 ha sem conflito.
Uso: python3 d01_tela.py <pasta gen37 com _render montado> <pasta de saída> [espelho]"""
import sys, os, time, subprocess, json
G=os.path.abspath(sys.argv[1]); OUTD=os.path.abspath(sys.argv[2]); ESP=len(sys.argv)>3; sys.path.insert(0,G); os.makedirs(OUTD,exist_ok=True)
from cdp import Chrome
from journeys import free
R=os.path.join(G,'_render'); p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
SEQ='Em sequência: divide trator, implemento ou operador'; PAR='Ao mesmo tempo, com recursos próprios'
CLK="""(t,root)=>{ const r=root?document.querySelector(root):document; const b=[...(r||document).querySelectorAll('button,a,[role=button]')].filter(x=>x.offsetParent&&x.innerText.replace(/\\s+/g,' ').trim()===t)[0]; if(!b) return 'sem '+t; b.click(); return 'ok'; }"""
OUT={}; c=None
try:
    c=Chrome(port=free()); J=c.js; B=f'http://127.0.0.1:{p}/'
    c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__err=[];addEventListener('error',e=>window.__err.push(String(e.message)));"})
    clk=lambda t,root=None,w=.45: (J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"),time.sleep(w))[0]
    T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def etapa(n): J(f"(()=>{{const b=[...document.querySelectorAll('nav[aria-label^=\"Etapas\"] button')].find(b=>b.innerText.replace(/\\s+/g,' ').trim().startsWith('{n} ')); if(b) b.click();}})()"); time.sleep(.5)
    def rows(): return J("[...document.querySelectorAll('[role=row]')].filter(r=>r.offsetParent).map(r=>[...r.querySelectorAll('[role=cell]')].map((x,i)=>{ const t=x.innerText.replace(/\\s+/g,' ').trim(); return i===0?t.replace(/^[▸▾]\\s*/,''):t; }))") or []
    def rec(t): J(f"(()=>{{const b=[...document.querySelectorAll('button[aria-label]')].filter(x=>x.offsetParent).find(b=>b.getAttribute('aria-label')==='Recolher '+{json.dumps(t)}); if(b) b.click();}})()"); time.sleep(.3)
    def exp(t): J(f"(()=>{{const b=[...document.querySelectorAll('button[aria-label]')].filter(x=>x.offsetParent).find(b=>b.getAttribute('aria-label')==='Expandir '+{json.dumps(t)}); if(b) b.click();}})()"); time.sleep(.35)
    def abrir(pref):
        r=J(f"(()=>{{const rs=[...document.querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent&&x.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(pref)})); const r=rs[0]; if(!r) return 'sem linha'; r.querySelector('[role=cell] span').click(); return 'ok';}})()"); time.sleep(.45); return r
    def campo(k,v):
        return J(f"""(()=>{{const i=document.querySelector('aside [id$="_{k}"]'); if(!i) return 'sem campo {k}'; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
          Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(v)}); i.dispatchEvent(new Event(i.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()""")
    def salvar(): return clk('Salvar','aside[role=dialog]'), T()
    def abrirEm(grupo,pred):
        r=J(f"""(()=>{{const rs=[...document.querySelectorAll('[role=row]')].filter(x=>x.offsetParent); const cs=x=>[...x.querySelectorAll('[role=cell]')].map(c=>c.innerText.replace(/\\s+/g,' ').trim());
          const i=rs.findIndex(x=>(cs(x)[0]||'').replace(/^[▸▾]\\s*/,'').startsWith({json.dumps(grupo)})); if(i<0) return 'sem grupo'; const P={pred};
          const r=rs.slice(i+1).find(x=>x.classList.contains('g2ed')&&(cs(x)[0]||'').startsWith('Parte:')&&P(cs(x)[1]||'')); if(!r) return 'sem linha'; r.querySelector('[role=cell] span').click(); return 'ok';}})()"""); time.sleep(.45); return r
    def so(op,atv):
        etapa(4)
        for o in ('Pulverização','Plantio','Adubação a lanço','Tratamento de sementes'):
            if o!=op: rec(o)
        exp(op); exp(atv)
        for l in (J("[...document.querySelectorAll('button[aria-label^=\"Expandir T\"]')].filter(b=>b.offsetParent).map(b=>b.getAttribute('aria-label'))") or []):
            J(f"(()=>{{const b=document.querySelector('button[aria-label={json.dumps(l)}]'); if(b) b.click();}})()"); time.sleep(.3)
        return rows()
    def t7():
        rs=so('Pulverização','Controle de ácaro'); i=next((k for k,r in enumerate(rs) if r and r[0].startswith('T7 ·')),None)
        return (rs[i],rs[i+1:i+5]) if i is not None else (None,[])
    c.size(1440,1000); c.goto(B+'SAF.dc.html#saf=S2627&etapa=3',wait=1.6)
    abrir('Controle de ácaro')
    for k,v in [('esc','Só esta atividade'),('modo','Largura × velocidade'),('larg','6'),('vel','8'),('efic','75'),('maq','180'),('impl','0'),('pess','0'),('pess_rs','0'),('jan','3')]: campo(k,v)
    OUT['A']=salvar()
    def outra(grupo):   # "+ Outra configuração" da linha do grupo (depois da 2ª configuração a atividade vira grupo)
        return J(f"""(()=>{{const rs=[...document.querySelectorAll('[role=row]')].filter(x=>x.offsetParent); const r=rs.find(x=>{{const c=x.querySelector('[role=cell]'); return c&&c.innerText.replace(/\s+/g,' ').trim().replace(/^[▸▾]\s*/,'').startsWith({json.dumps(grupo)});}});
          if(!r) return 'sem grupo'; const b=[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='+ Outra configuração'); if(!b) return 'sem botão'; b.click(); return 'ok';}})()""")
    for i,(nome,larg,jan) in enumerate((('B prestador 12 m','12','3'),('C prestador 6 m','6','3'),('D prestador 6 m','6','100'))):
        if i==0: abrir('Controle de ácaro'); OUT['abre '+nome]=clk('+ Outra configuração para Controle de ácaro','aside[role=dialog]')
        else: OUT['abre '+nome]=outra('Controle de ácaro'); time.sleep(.5)
        campo('conj_id','prestador'); time.sleep(.2)
        for k,v in [('nome',nome),('modo','Largura × velocidade'),('larg',larg),('vel','8'),('efic','75'),('maq','300'),('seq',SEQ),('jan',jan)]: campo(k,v)
        OUT[nome]=salvar()
    OUT['A seq']=(abrirEm('Controle de ácaro',"t=>t.indexOf('prestador')<0"),campo('seq',SEQ),salvar())
    oc,ks=t7(); OUT['seq_T7']=oc; OUT['seq_cfgs']=ks; c.shot(os.path.join(OUTD,'d01_sequencia_T7.png'))
    # controle positivo: as quatro ao mesmo tempo (recursos próprios)
    etapa(3)
    for pred in ("t=>t.indexOf('prestador')<0","t=>t.indexOf('B prestador')>=0","t=>t.indexOf('C prestador')>=0","t=>t.indexOf('D prestador')>=0"):
        OUT['par '+pred]=(abrirEm('Controle de ácaro',pred),campo('seq',PAR),salvar())
    oc2,ks2=t7(); OUT['par_T7']=oc2; OUT['par_cfgs']=ks2; c.shot(os.path.join(OUTD,'d01_controle_ao_mesmo_tempo_T7.png'))
    OUT['erros_js']=J("window.__err||[]")
finally:
    if c: c.close()
    srv.terminate()
if ESP:
    import dados2 as D2
    rA=D2.rend_calc(6,8,75); rB=D2.rend_calc(12,8,75)
    e=D2.repartir(42,[dict(nome='A',rend=rA,custo_h=180,jan=3,seq=True),dict(nome='B',rend=rB,custo_h=300,jan=3,seq=True),dict(nome='C',rend=rA,custo_h=300,jan=3,seq=True),dict(nome='D',rend=rA,custo_h=300,jan=100,seq=True)])
    e2=D2.repartir(42,[dict(nome='A',rend=rA,custo_h=180,jan=3),dict(nome='B',rend=rB,custo_h=300,jan=3),dict(nome='C',rend=rA,custo_h=300,jan=3),dict(nome='D',rend=rA,custo_h=300,jan=100)])
    OUT['espelho_seq']=dict(q=[round(x['q'],4) for x in e['itens']],h=[round(x['h'],4) for x in e['itens']],conflito=e['conflito'],deficit=round(e['deficit'],4),motivos=e['motivos'])
    OUT['espelho_par']=dict(q=[round(x['q'],4) for x in e2['itens']],conflito=e2['conflito'],motivos=e2['motivos'])
print(json.dumps(OUT,ensure_ascii=False,indent=1))
