# -*- coding: utf-8 -*-
"""Teste CDP · QUALIDADE-ARTEFATO-20261003-FLUXO item 1 (continuidade SAF → CMP) e item 2 (CAL-01 na tela).
Safrinha 2027 → etapa 6 → Enviar para cotação gera SOL-2027-02 com o registro único (talhao-os-compras-v1: ID, fazenda, safra, itens,
estado e origem) → "Abrir SOL-2027-02 ›" abre a MESMA solicitação (CMP.dc.html#sol=…&saf=…) no detalhe com os mesmos itens, valor e a
necessidade do CAL-01 (a memória fica só no Planejar safra, SUP §7) → recarregar mantém → a origem volta ao Planejar safra. Cada safra guarda o próprio andamento da compra, que
sobrevive à ida e volta (registro proc) e aparece no Planejar safra. Lagoa Grande: realizado fora da demanda, fazenda certa, grupos sem
homologado não travam os convites. Paridade da tela (safra.js) com dados2.demanda e bordas de endereço. Erros JS por ouvinte próprio.
Uso: python3 saf_cmp_continuidade_test.py [pasta_png]   (≈ 100 s; capturas q_saf-cmp_*.png em _probe/)"""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
R=os.path.join(HERE,'_render'); OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_probe'); os.makedirs(OUT,exist_ok=True)
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
OK=[]; FAIL=[]
def chk(nome,cond,det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ')+nome+('' if cond else f' · {str(det)[:400]}'),flush=True)
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
c=Chrome(port=free()); J=c.js; B=f'http://127.0.0.1:{p}/'
# erros JS da página: ouvinte instalado antes de cada documento; coletado antes de cada navegação e no fim
c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__err=[];addEventListener('error',e=>window.__err.push(String(e.message)));addEventListener('unhandledrejection',e=>window.__err.push(String(e.reason)));"})
ERR=[]
def col():
    try: ERR.extend(J("location.href==='about:blank'?[]:(window.__err||['sem ouvinte em '+location.pathname])") or [])
    except Exception as e: ERR.append('coleta: '+str(e))
import dados2 as D2
try:
    clk=lambda t,root=None,w=.45: (J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"),time.sleep(w))[0]
    T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    cur=lambda: J("(document.querySelector('[aria-current=step]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    body=lambda: J("document.body.innerText") or ''
    url=lambda: J("location.pathname+location.hash") or ''
    rowtxt=lambda t: J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].filter(x=>x.offsetParent).find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(t)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'sem linha';}})()") or ''
    def rowclick(t): r=J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(t)})>=0); if(!r) return 'sem linha'; (r.querySelector('[role=cell] b')||r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.45); return r
    def cel(nome,col):   # TABELAS-FOCO: valor de uma coluna (cabeçalho) na linha cujo Insumo é nome
        return J(f"""(()=>{{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());
          const iI=hs.indexOf('INSUMO'), i=hs.indexOf({json.dumps(col.upper())}); const r=[...t.querySelectorAll('[role=row]')].filter(x=>x.offsetParent).find(x=>{{const cs=x.querySelectorAll('[role=cell]'); return cs[iI]&&cs[iI].innerText.replace(/\\s+/g,' ').trim()==={json.dumps(nome)};}});
          return r?[...r.querySelectorAll('[role=cell]')][i].innerText.replace(/\\s+/g,' ').trim():'';}})()""") or ''
    def memo():   # linhas da memória CAL-01 no painel de origem do insumo (do estoque apto até o resultado)
        ls=[x.strip() for x in (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').split('\n') if x.strip()]
        i=next((k for k,x in enumerate(ls) if x.startswith('Estoque apto hoje')),None); j=next((k for k,x in enumerate(ls) if x.startswith('Necessidade líquida =') or x.startswith('Sem falta nesta safra') or x.startswith('Sem compra nova')),None)
        return ls[i:j+1] if i is not None and j is not None else ls
    def fechar(): J("(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return; const b=[...a.querySelectorAll('button')].find(b=>/^Fechar$|^×$/.test(b.innerText.trim())||b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()"); time.sleep(.35)
    def ir(f,w=1.2): col(); c.goto('about:blank',wait=.1); c.goto(B+f,wait=w)
    def esperar(pg):
        for _ in range(40):
            if J(f"location.pathname.endsWith('{pg}')&&document.readyState==='complete'&&document.body.innerText.length>200"): break
            time.sleep(.25)
        time.sleep(1.0)
    def nav(t,pg): col(); clk(t,w=.2); esperar(pg)
    trail=lambda: (J("(document.body.innerText.match(/DOCUMENTOS DA COMPRA[^\\n]*(\\n[^\\n]+){0,6}/)||[''])[0]") or '').replace('\n',' ')
    from comp_lib import IR_ETAPA
    def etapa(i): J(f"({IR_ETAPA})({i})"); time.sleep(.5)   # a faixa só informa: anda pela área de ações (UX-ACAO-UNICA-20261003)
    def foto(nome): c.shot(os.path.join(OUT,f'q_saf-cmp_{nome}.png'))
    def ls(): return json.loads(J("localStorage.getItem('talhao-os-compras-v1')||'null'") or 'null')
    c.size(1440,1000); ir('SAF.dc.html'); J("localStorage.clear()"); ir('SAF.dc.html')
    # ---------------- Planejar safra · Safrinha 2027 · etapa 6 ----------------
    r=J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safrinha 2027')>=0); const b=r&&[...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); if(!b) return 'sem botão'; b.click(); return b.innerText.trim();})()"""); time.sleep(.6)
    chk('1 SAF: Safrinha 2027 abre direto na etapa 6 ("Continuar: enviar demanda para cotação")',r=='Continuar: enviar demanda para cotação' and cur().startswith('6 '),(r,cur()))
    k6=J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]")
    chk('2 SAF etapa 6 (CAL-01): R$ 1.098.502,50 · 8 insumos a comprar · ainda não enviada',k6=='Valor da necessidade líquida R$ 1.098.502,50 · 8 insumos a comprar · ainda não enviada',k6)
    clk('Expandir tudo'); mp=rowtxt('MAP 11-52')
    # TABELAS-FOCO (5983172395): necessidade, unidade, data da falta e "usado antes" em colunas próprias
    # a unidade fica junto do valor (decisão do proprietário, 05/10/2026); data da falta e "usado antes" em colunas próprias
    mpc=[cel('MAP 11-52',k) for k in ('Necessidade líquida','Falta em','Usado antes da compra')]
    chk('3 SAF MAP 11-52: 101.440 kg com falta em 20/02/2027 · estoque apto 90.000 usado antes',mpc==['101.440 kg','20/02/2027','90.000 kg'],(mpc,mp))
    rowclick('MAP 11-52'); m_saf=memo(); fechar()
    chk('4 SAF memória MAP: estoque apto, usos da Safra 2026/27 antes, resultado com a data',m_saf[:1]==['Estoque apto hoje: 90.000 kg'] and any(l.startswith('15/10/2026 · Safra 2026/27 · 1 uso · −') for l in m_saf)
        and m_saf[-1]=='Necessidade líquida = soma das faltas desta safra = 101.440 kg · falta a partir de 20/02/2027',m_saf)
    foto('1_saf_etapa6')
    clk('Enviar para cotação'); t=T()
    chk('5 SAF envia SOL-2027-02: 8 insumos, R$ 1.098.502,50, origem Safrinha 2027 · etapa 6',t.startswith('Solicitação SOL-2027-02 enviada a Compras: 8 insumos, R$ 1.098.502,50. Origem: Safrinha 2027 · Planejar safra, etapa 6.'),t)
    g=ls(); s=((g or {}).get('sols') or {}).get('S27SF') or {}
    chk('6 registro único talhao-os-compras-v1: ID, fazenda, safra, 8 itens, estado e origem',s.get('id')=='SOL-2027-02' and s.get('safra')=='S27SF' and s.get('nome')=='Safrinha 2027' and s.get('faz')=='Santa Rita'
        and len(s.get('itens') or {})==8 and s.get('estado')=='Enviada · a cotar' and (s.get('origem') or {}).get('h')=='SAF.dc.html#saf=S27SF&etapa=6' and abs((s.get('total') or 0)-1098502.5)<0.01,
        {k:s.get(k) for k in ['id','safra','nome','faz','estado','origem','total']})
    clk('Enviar para cotação') if J("[...document.querySelectorAll('button')].some(b=>b.offsetParent&&b.innerText.trim()==='Enviar para cotação')") else None
    # SUP §7 (06/10): o atalho nomeia a solicitação (antes "Abrir Compra de insumos ›")
    chk('7 SAF: tudo enviado, a ação principal vira "Abrir SOL-2027-02 ›" (sem duplicar)',J("[...document.querySelectorAll('button,a')].filter(b=>b.offsetParent).some(b=>b.innerText.trim()==='Abrir SOL-2027-02 ›')") and len((ls() or {}).get('sols',{}))==1)
    foto('2_saf_enviado')
    # ---------------- Compras · a mesma solicitação (SUP: lista de solicitações → detalhe na fase; eram 6 etapas) ----------------
    faixa=lambda: (J("(document.querySelector('[aria-label=\"Situação da solicitação\"]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or '')
    prim=lambda: (J("(()=>{const b=[...document.querySelectorAll('.acoes-prim')].find(b=>b.offsetParent); return b?b.innerText.trim():'';})()") or '')
    def clk_prim(): J("(()=>{const b=[...document.querySelectorAll('.acoes-prim')].find(b=>b.offsetParent); if(b) b.click();})()"); time.sleep(.6)
    def lista(): clk('‹ Solicitações'); time.sleep(.3)
    def abre_sol(sol): rowclick(sol); time.sleep(.4)
    def ccel(lin,col): return J(f"(()=>{{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase()); const r=[...t.querySelectorAll('[role=row]')].filter(x=>x.offsetParent).find(x=>x.innerText.indexOf({json.dumps(lin)})>=0); if(!r) return 'sem linha'; const c=[...r.querySelectorAll('[role=cell]')][hs.indexOf({json.dumps(col.upper())})]; return c?c.innerText.replace(/\\s+/g,' ').trim():'sem coluna';}})()") or ''
    def respostas(t=14):
        for _ in range(int(t/.5)):
            if 'Em cotação' not in faixa(): break
            time.sleep(.5)
        time.sleep(.4)
    nav('Abrir SOL-2027-02 ›','CMP.dc.html')
    chk('8 Compras abre a mesma solicitação: #sol=SOL-2027-02&saf=S27SF, detalhe "A cotar" com a origem Safrinha 2027',url()=='/CMP.dc.html#sol=SOL-2027-02&saf=S27SF' and 'SOL-2027-02' in faixa() and 'Safrinha 2027' in faixa() and 'A cotar' in faixa(),(url(),faixa()[:200]))
    lista(); it_=ccel('SOL-2027-02','Itens'); vl_=ccel('SOL-2027-02','Valor ref.')
    chk('9 lista de Compras: SOL-2027-02 com os mesmos 8 insumos e R$ 1.098.502,50',it_=='8' and vl_=='R$ 1.098.502,50',(it_,vl_))
    foto('3_cmp_lista')
    ir('CMP.dc.html#sol=SOL-2027-02&saf=S27SF',w=1.4)
    chk('13 recarregar Compras mantém a SOL-2027-02 aberta',url()=='/CMP.dc.html#sol=SOL-2027-02&saf=S27SF' and 'SOL-2027-02' in faixa() and 'Safrinha 2027' in faixa(),(url(),faixa()[:160]))
    # cada safra guarda o próprio andamento: convites da 2026/27 não aparecem na Safrinha
    lista(); abre_sol('SOL-2026-07'); clk_prim(); k3a=T(); time.sleep(2.5)
    lista(); abre_sol('SOL-2027-02'); p3=prim()
    chk('15 Safrinha não herda os convites da 2026/27 (segue "A cotar" com os convites prontos) e o endereço acompanha a safra','Convites simulados' in k3a and 'A cotar' in faixa() and p3.startswith('Enviar ') and url()=='/CMP.dc.html#sol=SOL-2027-02&saf=S27SF',(k3a[:80],faixa()[:120],p3,url()))
    n13=p3; clk_prim(); respostas(); clk('Expandir tudo')
    mp2=[ccel('MAP 11-52',k) for k in ('A pedir','Falta em')]
    chk('16 cotação da SOL-2027-02 segue: propostas chegam e a fase vira Decida (Semente de milho AG 8700 na comparação)','Em cotação' not in faixa() and 'Semente de milho AG 8700' in body(),(faixa()[:160]))
    chk('10 Compras MAP 11-52: 101.440 kg a pedir com falta em 20/02/2027 (mesmo número do CAL-01 no Planejar safra)',mp2==['101.440 kg','20/02/2027'],mp2)
    rowclick('MAP 11-52'); og=(J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or ''); lk=J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>[a.innerText.trim(),a.getAttribute('href')])") or []; fechar()
    chk('11 a necessidade em Compras = resultado da memória CAL-01 do Planejar safra (101.440 kg); a memória fica só lá (SUP §7)','= 101.440 kg' in og and m_saf[-1].startswith('Necessidade líquida = soma das faltas desta safra = 101.440 kg'),(og[:300],m_saf[-1:]))
    chk('12 "Ver memória no Planejar safra" volta à demanda da Safrinha',any(t=='Ver memória no Planejar safra' and (h or '').startswith('SAF.dc.html#saf=S27SF') for t,h in lk),lk)
    foto('3b_cmp_decida')
    lista(); abre_sol('SOL-2026-07'); e7=faixa()
    chk('17 de volta à 2026/27: os convites dela continuam enviados (não volta a "A cotar")','A cotar' not in e7 and 'SOL-2026-07' in e7,e7[:160])
    # ---------------- volta à origem ----------------
    lista(); abre_sol('SOL-2027-02')
    h=J("(()=>{const a=[...document.querySelectorAll('[aria-label=\"Situação da solicitação\"] a')].find(a=>a.offsetParent); return a?a.getAttribute('href'):'';})()") or ''
    chk('18 a faixa do detalhe oferece a origem (Planejar safra da Safrinha)',h.startswith('SAF.dc.html#saf=S27SF'),h)
    g0=ls() or {}; e0=(g0.get('proc') or {}).get('S27SF',{}).get('estado','')
    col(); J("(()=>{const a=[...document.querySelectorAll('[aria-label=\"Situação da solicitação\"] a')].find(a=>a.offsetParent); a&&a.click();})()"); esperar('SAF.dc.html')
    k6b=J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]")
    chk('19 SAF volta na Safrinha e mostra o andamento da compra lido do registro (proc): "solicitação SOL-2027-02 · <situação de Compras>"',e0 not in ('','A cotar') and ('solicitação SOL-2027-02 · '+e0) in k6b,(e0,k6b))
    foto('5_saf_volta')
    nav('Abrir SOL-2027-02 ›','CMP.dc.html'); g=ls() or {}
    chk('26 Compras → origem → Compras: convites e propostas da SOL-2027-02 continuam e o registro guarda o estado',
        'Em cotação' not in faixa() and 'A cotar' not in faixa() and (g.get('proc') or {}).get('S27SF',{}).get('estado','')==e0 and (g.get('sols') or {}).get('S27SF',{}).get('estado','')==e0,
        {'faixa':faixa()[:120],'proc':(g.get('proc') or {}).get('S27SF',{}).get('estado'),'sol':(g.get('sols') or {}).get('S27SF',{}).get('estado')})
    ir('SAF.dc.html'); px=rowtxt('Safrinha 2027')
    chk('20 SAF recarregada sem endereço: a Safrinha não volta a "enviar demanda" (registro mantido)','enviar demanda' not in px and 'Continuar' in px,px)
    # ---------------- mesma memória na Safra 2026/27 (reserva de outro destino) ----------------
    J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safra 2026/27')>=0); [...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())).click();})()"""); time.sleep(.5)
    etapa(6); w=J("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const box=t.parentElement; return {box:box.clientWidth, scroll:box.scrollWidth, tab:Math.round(t.getBoundingClientRect().width)};})()")
    hs=J("[...[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent).querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' ').replace(/ ⇅.*$/,'').trim())") or []
    # TABELAS-FOCO item 6: com uma variável por coluna a tabela pode rolar dentro da caixa; a página não rola e "1º uso" segue logo depois do insumo (v3.8)
    pg=J("[document.documentElement.scrollWidth, innerWidth]")
    # com a rolagem no início, as colunas essenciais da compra ficam à vista dentro da caixa (não basta a página não rolar)
    vis=J("""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const box=t.parentElement; box.scrollLeft=0; const R=box.getBoundingClientRect();
      return [...t.querySelectorAll('[role=columnheader]')].filter(h=>R.right+0.5>=h.getBoundingClientRect().right).map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());})()""") or []
    ess=['GRUPO','INSUMO','1º USO','NECESSIDADE LÍQUIDA','FALTA EM']
    chk('23 SAF etapa 6 (2026/27, grupos recolhidos): a página não rola; "1º uso" logo depois de Grupo | Insumo (v3.8); Necessidade líquida e Falta em à vista sem rolar a tabela',
        pg[0]<=pg[1]+1 and len(hs)>3 and [h.upper() for h in hs[:3]]==['GRUPO','INSUMO','1º USO'] and all(x in vis for x in ess),(w,pg,hs[:4],vis))
    clk('Expandir tudo'); fa=rowtxt('Fungicida A'); gl=rowtxt('Glifosato 480'); rowclick('Glifosato 480'); gm=memo(); fechar()
    chk('24 memória como extrato por data, com a origem de sempre: "25/09/2026 · T1-A · Dessecação pré-plantio · 2,00 L/ha × 160 ha = 320,0 L"; 1º uso intacto',
        any(l.startswith('25/09/2026 · T1-A · Dessecação pré-plantio · 2,00 L/ha × 160 ha = 320,0 L → saldo') for l in gm) and cel('Glifosato 480','1º uso')=='25/09/2026',(gl,gm[:3]))
    rowclick('Fungicida A'); fs=memo(); fechar(); fa=fa+' | '+' · '.join(cel('Fungicida A',k) for k in ('Estoque apto','Usado antes da compra','Necessidade líquida'))
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.4); respostas(); clk('Expandir tudo'); fa2=ccel('Fungicida A','A pedir'); rowclick('Fungicida A'); fc=(J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or ''); fechar()
    chk('21 Fungicida A (2026/27): estoque apto 545 (65 reservados à OS-0424, usados antes); 145,2 L no Planejar safra e a pedir em Compras',
        fa.endswith(' | 545,0 L · 65,0 L · 145,2 L') and fa2=='145,2 L' and '= 145,2 L' in fc and any(l.startswith('24/09/2026 · Reserva REQ-039 · OS-0424 (T1-B) · −65,0 L') for l in fs),{'fa':fa,'fa2':fa2,'cmp':fc[:200],'saf':fs[-2:]})
    # safra criada no Planejar safra (fora do cadastro da Compra): a solicitação gravada aparece na lista e abre com contexto próprio
    J("""(()=>{const o=JSON.parse(localStorage.getItem('talhao-os-compras-v1')); const r=JSON.parse(JSON.stringify(o.sols.S27SF)); r.safra='n9'; r.nome='Safra nova teste'; r.id='SOL-2026-10'; o.sols.n9=r; localStorage.setItem('talhao-os-compras-v1',JSON.stringify(o));})()""")
    ir('CMP.dc.html#sol=SOL-2026-10&saf=n9',w=1.4); fxn=faixa()
    lista(); rn=rowtxt('SOL-2026-10')
    chk('25 solicitação de safra nova (só no Planejar safra) aparece na lista de Compras e abre com o próprio contexto','SOL-2026-10' in fxn and 'Safra nova teste' in fxn and 'Safra nova teste' in rn,(fxn[:160],rn))
    # ---------------- paridade da tela (safra.js + cal01.js) com dados2.demanda (Python) ----------------
    par=[]
    for saf in ['S2627','S27SF','LG2627']:
        ir(f'SAF.dc.html#saf={saf}&etapa=6',w=1.4); k6=J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]") or ''
        dm=D2.demanda(saf); n=sum(1 for o in dm.values() if o['liq']>0.001); tot=sum(o['valor'] for o in dm.values())
        esp='R$ '+f"{tot:,.2f}".replace(',','X').replace('.',',').replace('X','.')+f' · {n} insumos a comprar'; par.append((saf,esp in k6,esp,k6))
    chk('27 paridade na tela: etapa 6 de S2627, S27SF e LG2627 = dados2.demanda (valor e nº de insumos)',all(x[1] for x in par),par)
    # ---------------- Lagoa Grande: realizado fora da demanda, fazenda certa, convites sem trava ----------------
    ir('SAF.dc.html#saf=LG2627&etapa=6',w=1.6); clk('Expandir tudo'); cal=rowtxt('Calcário dolomítico filler'); fz=J("[...document.querySelectorAll('span')].filter(s=>s.children.length===0&&/^Fazenda /.test(s.innerText.trim())).map(s=>s.innerText.trim())")
    # falta com necessidade líquida (a ruptura coberta pelo recebimento não conta): data da coluna "Falta em" antes de hoje
    passadas=J("""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());
      const iF=hs.indexOf('FALTA EM'), iL=hs.indexOf('NECESSIDADE LÍQUIDA'); return [...t.querySelectorAll('[role=row]')].map(r=>[...r.querySelectorAll('[role=cell]')].map(c=>c.innerText.trim())).filter(c=>c.length>iF&&/^\\d\\d\\/\\d\\d\\/\\d{4}$/.test(c[iF])&&c[iL]&&!/^0(,0+)?( |$)/.test(c[iL])).map(c=>c[iF]).filter(s=>{const m=s.split('/'); return (m[2]+m[1]+m[0])<'20260923';});})()""")
    # números do calcário pelo espelho dados2.demanda (área da fonte da Lagoa; PRE-REV R6: antes eram fixos da área antiga)
    cdm=D2.demanda('LG2627')['Calcário dolomítico filler']; nk=lambda v: f"{v:,.0f}".replace(',','.'); dm_=lambda iso: iso[8:10]+'/'+iso[5:7]
    rup_=f"ruptura {dm_(cdm['falta'])}–{dm_(cdm['cob'])}"
    def calagem_ok(mc):   # a linha da calagem que rompe mostra a área do pivô com até 2 casas (PRE-REV R5: antes, inteira)
        import re as _re, dados_lagoa_fonte as _F
        ln=next((l for l in mc if l.startswith(f"{dm_(cdm['falta'])}/{cdm['falta'][:4]} · Pivô ")),''); m=_re.search(r'Pivô (\d+)',ln)
        return bool(m) and f"× {D2._nfa(_F.PIVOS_HA[int(m.group(1))])} ha" in ln
    chk(f"28 SAF Mamão 2026/27: Fazenda Lagoa Grande; nenhuma falta antes de hoje; calcário com {nk(cdm['real'])} realizados, {rup_} coberta pelo recebimento, 0 a comprar (= dados2.demanda)",
        fz==['Fazenda Lagoa Grande'] and not passadas and cdm['liq']==0 and cdm['rup']>0
        and [cel('Calcário dolomítico filler',k) for k in ('Já realizado','Falta em','Coberta em','Situação','Demanda bruta')]==[nk(cdm['real'])+' kg',dm_(cdm['falta'])+'/'+cdm['falta'][:4],dm_(cdm['cob'])+'/'+cdm['cob'][:4],'Coberto pelo recebimento',nk(cdm['bruta'])+' kg'],
        (fz,passadas,cal,[cel('Calcário dolomítico filler',k) for k in ('Já realizado','Falta em','Coberta em','Situação','Demanda bruta')]))
    rowclick('Calcário dolomítico filler'); mc=memo(); fechar(); foto('7_saf_lg_etapa6')
    chk('29 memória do calcário: realizado antes de hoje, ruptura na calagem de 25/09, recebimento de 30/09 cobre, sem compra nova',
        len(mc)>2 and mc[1].startswith('Realizado antes de 23/09/2026 · ') and any(l.startswith('30/09/2026 · ') and l.endswith('cobre a ruptura') for l in mc)
        and mc[-1]==f"Sem compra nova · ruptura de {nk(cdm['rup'])} kg de {dm_(cdm['falta'])}/{cdm['falta'][:4]} a {dm_(cdm['cob'])}/{cdm['cob'][:4]}, coberta pelo recebimento"
        and calagem_ok(mc),mc)
    clk('Enviar para cotação'); tl=T(); nav('Abrir SOL-2026-09 ›','CMP.dc.html')
    fz2=J("[...document.querySelectorAll('span')].filter(s=>s.children.length===0&&/^Fazenda /.test(s.innerText.trim())).map(s=>s.innerText.trim())")
    cg=[rowtxt('Corretivos'),rowtxt('Mudas')]; clk_prim(); tc=T(); respostas(); fx=faixa(); foto('8_cmp_lg_cote')
    chk('30 Compras da SOL-2026-09: Fazenda Lagoa Grande; Corretivos e Mudas "Sem fornecedor homologado" com link de cadastro; convites dos outros grupos saem e as propostas chegam',
        tl.startswith('Solicitação SOL-2026-09 enviada a Compras: 12 insumos') and fz2==['Fazenda Lagoa Grande'] and all('Sem fornecedor homologado' in x and 'Cadastrar em Parceiros e fornecedores' in x for x in cg)
        and tc.startswith('Convites simulados') and tc.endswith('Sem cotação (sem fornecedor homologado): Corretivos, Mudas.') and 'A cotar' not in fx and 'Em cotação' not in fx,(tl,fz2,cg,tc,fx[:160]))
    # ---------------- bordas de endereço ----------------
    ir('CMP.dc.html#sol=SOL-9999&saf=S27SF',w=1.4); b1=(url(),faixa(),T())
    ir('CMP.dc.html#saf=S2526',w=1.4); b2=(url(),J("(document.querySelector('nav[aria-label=\"Seções de compras\"] button[aria-current=true]')||{innerText:''}).innerText.trim()") or '',T())
    chk('31 endereço com SOL de outra safra abre a SOL da safra e corrige o endereço; safra encerrada por endereço abre Acompanhe pedidos',
        b1[0]=='/CMP.dc.html#sol=SOL-2027-02&saf=S27SF' and 'SOL-2027-02' in b1[1] and b1[2]=='SOL-9999 não é a solicitação da Safrinha 2027: aberta a SOL-2027-02.'
        and b2[1].startswith('Acompanhe pedidos') and 'encerrada' in b2[2] and 'não está gravada' not in b2[2],(b1,b2))
    c.size(390,844); ir('CMP.dc.html#sol=SOL-2027-02&saf=S27SF',w=1.4); foto('6_cmp_390'); col()
    chk('22 sem erro JS (ouvinte de error e unhandledrejection em cada página aberta)', ERR==[], ERR[:5])
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)
