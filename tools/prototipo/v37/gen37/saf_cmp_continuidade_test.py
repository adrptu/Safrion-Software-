# -*- coding: utf-8 -*-
"""Teste CDP · QUALIDADE-ARTEFATO-20261003-FLUXO item 1 (continuidade SAF → CMP) e item 2 (CAL-01 na tela).
Safrinha 2027 → etapa 6 → Enviar para cotação gera SOL-2027-02 com o registro único (talhao-os-compras-v1: ID, fazenda, safra, itens,
estado e origem) → Abrir Compra de insumos abre a MESMA solicitação (CMP.dc.html#sol=…&saf=…) na etapa 2 com os mesmos itens, valor e
memória CAL-01 → recarregar mantém → Ver origem volta ao Planejar safra na etapa 6. Cada safra guarda o próprio andamento da compra, que
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
    def etapa(i): J(f"document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[{i-1}].click()"); time.sleep(.5)
    def foto(nome): c.shot(os.path.join(OUT,f'q_saf-cmp_{nome}.png'))
    def ls(): return json.loads(J("localStorage.getItem('talhao-os-compras-v1')||'null'") or 'null')
    c.size(1440,1000); ir('SAF.dc.html'); J("localStorage.clear()"); ir('SAF.dc.html')
    # ---------------- Planejar safra · Safrinha 2027 · etapa 6 ----------------
    r=J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safrinha 2027')>=0); const b=r&&[...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); if(!b) return 'sem botão'; b.click(); return b.innerText.trim();})()"""); time.sleep(.6)
    chk('1 SAF: Safrinha 2027 abre direto na etapa 6 ("Continuar: enviar demanda para cotação")',r=='Continuar: enviar demanda para cotação' and cur().startswith('6 '),(r,cur()))
    k6=J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]")
    chk('2 SAF etapa 6 (CAL-01): R$ 1.098.502,50 · 8 insumos a comprar · ainda não enviada',k6=='Valor da necessidade líquida R$ 1.098.502,50 · 8 insumos a comprar · ainda não enviada',k6)
    clk('Expandir tudo'); mp=rowtxt('MAP 11-52')
    chk('3 SAF MAP 11-52: 101.440 kg com falta em 20/02/2027 · estoque apto 90.000 usado antes',all(x in mp for x in ['falta em 20/02/2027','101.440 kg','usado antes: 90.000']),mp)
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
    chk('7 SAF: tudo enviado, a ação principal vira "Abrir Compra de insumos ›" (sem duplicar)',J("[...document.querySelectorAll('button')].filter(b=>b.offsetParent).some(b=>b.innerText.trim()==='Abrir Compra de insumos ›')") and len((ls() or {}).get('sols',{}))==1)
    foto('2_saf_enviado')
    # ---------------- Compra de insumos · a mesma solicitação ----------------
    nav('Abrir Compra de insumos ›','CMP.dc.html')
    chk('8 CMP abre a mesma solicitação: #sol=SOL-2027-02&saf=S27SF, etapa 2, contexto "Safrinha 2027 · SOL-2027-02"',url()=='/CMP.dc.html#sol=SOL-2027-02&saf=S27SF' and cur().startswith('2 Confira a demanda') and 'Safrinha 2027 · SOL-2027-02' in body(),(url(),cur()))
    k2=J("(document.body.innerText.match(/SOL-2027-02 · Safrinha 2027[^\\n]+/)||[''])[0]"); tot=J("[...document.querySelectorAll('.g2tot')].filter(x=>x.offsetParent).map(x=>x.innerText).join(' ')") or ''
    chk('9 CMP etapa 2: mesmos 8 insumos e R$ 1.098.502,50 (resumo e total da tabela)','8 insumos a comprar · R$ 1.098.502,50 a preço de referência' in k2 and '1.098.502,50' in tot,(k2,tot))
    clk('Expandir tudo'); mp2=rowtxt('MAP 11-52')
    chk('10 CMP MAP 11-52: 101.440 · falta a partir de 20/02/2027 · estoque usado antes: 90.000',all(x in mp2 for x in ['101.440','20/02/2027','usado antes: 90.000']),mp2)
    rowclick('MAP 11-52'); m_cmp=memo(); lk=J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>[a.innerText.trim(),a.getAttribute('href')])") or []; foto('3b_cmp_memoria_cal01'); fechar()
    chk('11 mesma memória CAL-01 nas duas telas (MAP 11-52, linha a linha)',m_cmp==m_saf and len(m_saf)>=6,{'saf':m_saf,'cmp':m_cmp})
    chk('12 origem do insumo volta ao Planejar safra na etapa 6 da Safrinha',any(t.startswith('Ver no Planejar safra · etapa 6') and h=='SAF.dc.html#saf=S27SF&etapa=6' for t,h in lk),lk)
    foto('3_cmp_etapa2')
    ir('CMP.dc.html#sol=SOL-2027-02&saf=S27SF',w=1.4)
    chk('13 recarregar a Compra mantém SOL-2027-02 na etapa 2',cur().startswith('2 Confira a demanda') and 'Safrinha 2027 · SOL-2027-02' in body() and '1.098.502,50' in body(),(cur(),url()))
    etapa(1); sf=rowtxt('Safrinha 2027'); s7=rowtxt('Safra 2026/27')
    chk('14 CMP etapa 1: Safrinha com SOL-2027-02 · 8 insumos · R$ 1.098.502,50 · A cotar; 2026/27 continua SOL-2026-07 · R$ 379.580,00',
        all(x in sf for x in ['SOL-2027-02','8 insumos · R$ 1.098.502,50','A cotar','Abrir compra']) and 'Sem solicitação' not in sf and 'SOL-2026-07' in s7 and 'R$ 379.580,00' in s7,(sf,s7))
    foto('4_cmp_etapa1')
    # cada safra guarda o próprio andamento: convites da 2026/27 não aparecem na Safrinha
    J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safra 2026/27')>=0); [...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Abrir compra').click();})()"""); time.sleep(.5)
    etapa(3); clk('Enviar convites (simulado)'); time.sleep(2.5)
    k3a=J("(document.body.innerText.match(/Convites simulados[^\\n]+/)||[''])[0]")
    etapa(1); J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safrinha 2027')>=0); [...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Abrir compra').click();})()"""); time.sleep(.5)
    etapa(3); k3b=J("(document.body.innerText.match(/\\d+ convites prontos[^\\n]+/)||[''])[0]"); ctx=J("(document.body.innerText.match(/Safrinha 2027 · SOL-2027-02/)||[''])[0]")
    chk('15 Safrinha não herda os convites da 2026/27 (convites prontos, nada enviado) e o endereço acompanha a safra',bool(k3a) and bool(k3b) and ctx and url()=='/CMP.dc.html#sol=SOL-2027-02&saf=S27SF',(k3a,k3b,url()))
    clk('Enviar convites (simulado)'); time.sleep(3.5); etapa(4); k4=J("(document.body.innerText.match(/\\d+ propostas? · custo total[^\\n]+/)||[''])[0]")
    chk('16 cotação da SOL-2027-02 segue: convites enviados e propostas comparadas na etapa 4',cur().startswith('4 ') and bool(k4) and 'Semente de milho AG 8700' in body(),(cur(),k4))
    etapa(1); J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safra 2026/27')>=0); [...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Abrir compra').click();})()"""); time.sleep(.5)
    etapa(3); k3c=J("(document.body.innerText.match(/Convites simulados[^\\n]+/)||[''])[0]")
    chk('17 de volta à 2026/27: os convites dela continuam enviados',bool(k3c) and 'SOL-2026-07' in body(),k3c)
    # ---------------- volta à origem ----------------
    etapa(1); J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safrinha 2027')>=0); [...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Abrir compra').click();})()"""); time.sleep(.5)
    h=J("(()=>{const a=[...document.querySelectorAll('a')].find(a=>a.offsetParent&&a.innerText.trim()==='Ver origem · etapa 6 ›'); return a?a.getAttribute('href'):'';})()")
    chk('18 trilha da compra oferece "Ver origem · etapa 6 ›" para a Safrinha',h=='SAF.dc.html#saf=S27SF&etapa=6',h)
    tr0=trail(); nav('Ver origem · etapa 6 ›','SAF.dc.html')
    k6b=J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]")
    chk('19 SAF volta na etapa 6 da Safrinha e mostra o andamento da compra (registro proc): SOL-2027-02 · Em cotação · N de 13 respostas',cur().startswith('6 ') and 'Safrinha 2027' in J("document.body.innerText.slice(0,600)") and 'solicitação SOL-2027-02 · Em cotação · ' in k6b and 'de 13 respostas' in k6b,(cur(),k6b))
    foto('5_saf_volta')
    nav('Abrir Compra de insumos ›','CMP.dc.html'); tr1=trail(); g=ls() or {}
    chk('26 Compra → origem → Compra: convites e propostas da SOL-2027-02 continuam (trilha igual) e o registro guarda o estado',
        '13 convites enviados' in tr1 and ' 0 propostas' not in tr1 and tr1==tr0 and (g.get('proc') or {}).get('S27SF',{}).get('estado','').startswith('Em cotação') and (g.get('sols') or {}).get('S27SF',{}).get('estado','').startswith('Em cotação'),
        {'antes':tr0,'depois':tr1,'proc':(g.get('proc') or {}).get('S27SF',{}).get('estado'),'sol':(g.get('sols') or {}).get('S27SF',{}).get('estado')})
    ir('SAF.dc.html'); px=rowtxt('Safrinha 2027')
    chk('20 SAF recarregada sem endereço: a Safrinha não volta a "enviar demanda" (registro mantido)','enviar demanda' not in px and 'Continuar' in px,px)
    # ---------------- mesma memória na Safra 2026/27 (reserva de outro destino) ----------------
    J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safra 2026/27')>=0); [...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())).click();})()"""); time.sleep(.5)
    etapa(6); w=J("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const box=t.parentElement; return {box:box.clientWidth, scroll:box.scrollWidth, tab:Math.round(t.getBoundingClientRect().width)};})()")
    hs=J("[...[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent).querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' ').replace(/ ⇅.*$/,'').trim())") or []
    chk('23 SAF etapa 6 (2026/27, grupos recolhidos) não fica mais larga que antes (1.230 px na v42) e mantém "1º uso" logo depois de Grupo · insumo (v3.8)',w['tab']<=1230 and len(hs)>2 and hs[1].upper().startswith('1º USO'),(w,hs))
    clk('Expandir tudo'); fa=rowtxt('Fungicida A'); gl=rowtxt('Glifosato 480'); rowclick('Glifosato 480'); gm=memo(); fechar()
    chk('24 memória como extrato por data, com a origem de sempre: "25/09/2026 · T1-A · Dessecação pré-plantio · 2,00 L/ha × 160 ha = 320,0 L"; 1º uso intacto',
        any(l.startswith('25/09/2026 · T1-A · Dessecação pré-plantio · 2,00 L/ha × 160 ha = 320,0 L → saldo') for l in gm) and gl.startswith('Glifosato 480 25/09/2026'),(gl,gm[:3]))
    rowclick('Fungicida A'); fs=memo(); fechar()
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.4); clk('Expandir tudo'); fa2=rowtxt('Fungicida A'); rowclick('Fungicida A'); fc=memo(); fechar()
    chk('21 Fungicida A (2026/27): estoque apto 545 (65 reservados à OS-0424, usados antes); 145,2 L como antes; memória igual nas duas telas',
        '545,0 L' in fa and 'usado antes: 65,0' in fa and '145,2 L' in fa and 'usado antes: 65,0' in fa2 and '145,2' in fa2 and fs==fc and any(l.startswith('24/09/2026 · Reserva REQ-039 · OS-0424 (P2) · −65,0 L') for l in fs),{'fa':fa,'fa2':fa2,'iguais':fs==fc,'saf':fs[-2:],'cmp':fc[-2:]})
    # safra criada no Planejar safra (fora do cadastro da Compra): a solicitação gravada aparece na lista e abre com contexto próprio
    J("""(()=>{const o=JSON.parse(localStorage.getItem('talhao-os-compras-v1')); const r=JSON.parse(JSON.stringify(o.sols.S27SF)); r.safra='n9'; r.nome='Safra nova teste'; r.id='SOL-2026-10'; o.sols.n9=r; localStorage.setItem('talhao-os-compras-v1',JSON.stringify(o));})()""")
    ir('CMP.dc.html#sol=SOL-2026-10&saf=n9',w=1.4); ctxn=J("(document.body.innerText.match(/Safra nova teste · SOL-2026-10/)||[''])[0]"); cn=cur()
    etapa(1); rn=rowtxt('Safra nova teste')
    chk('25 solicitação de safra nova (só no Planejar safra) aparece na Compra e abre com o próprio contexto',ctxn=='Safra nova teste · SOL-2026-10' and cn.startswith('2 ') and 'SOL-2026-10' in rn and 'Abrir compra' in rn,(ctxn,cn,rn))
    # ---------------- paridade da tela (safra.js + cal01.js) com dados2.demanda (Python) ----------------
    par=[]
    for saf in ['S2627','S27SF','LG2627']:
        ir(f'SAF.dc.html#saf={saf}&etapa=6',w=1.4); k6=J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]") or ''
        dm=D2.demanda(saf); n=sum(1 for o in dm.values() if o['liq']>0.001); tot=sum(o['valor'] for o in dm.values())
        esp='R$ '+f"{tot:,.2f}".replace(',','X').replace('.',',').replace('X','.')+f' · {n} insumos a comprar'; par.append((saf,esp in k6,esp,k6))
    chk('27 paridade na tela: etapa 6 de S2627, S27SF e LG2627 = dados2.demanda (valor e nº de insumos)',all(x[1] for x in par),par)
    # ---------------- Lagoa Grande: realizado fora da demanda, fazenda certa, convites sem trava ----------------
    ir('SAF.dc.html#saf=LG2627&etapa=6',w=1.6); clk('Expandir tudo'); cal=rowtxt('Calcário dolomítico filler'); fz=J("[...document.querySelectorAll('span')].filter(s=>s.children.length===0&&/^Fazenda /.test(s.innerText.trim())).map(s=>s.innerText.trim())")
    passadas=J("(document.body.innerText.match(/falta em \\d\\d\\/\\d\\d\\/\\d{4}/g)||[]).filter(s=>{const m=s.match(/(\\d\\d)\\/(\\d\\d)\\/(\\d{4})/); return (m[3]+m[2]+m[1])<'20260923';})")
    chk('28 SAF Mamão 2026/27: Fazenda Lagoa Grande; nenhuma falta antes de hoje; calcário com 1.118.000 realizados, ruptura 25/09–30/09 coberta pelo recebimento, 0 a comprar',
        fz==['Fazenda Lagoa Grande'] and not passadas and all(x in cal for x in ['realizado: 1.118.000','ruptura 25/09–30/09','Coberto pelo recebimento','110.000 kg']),(fz,passadas,cal))
    rowclick('Calcário dolomítico filler'); mc=memo(); fechar(); foto('7_saf_lg_etapa6')
    chk('29 memória do calcário: realizado antes de hoje, ruptura na calagem de 25/09, recebimento de 30/09 cobre, sem compra nova',
        len(mc)>2 and mc[1].startswith('Realizado antes de 23/09/2026 · ') and any(l.startswith('30/09/2026 · ') and l.endswith('cobre a ruptura') for l in mc)
        and mc[-1]=='Sem compra nova · ruptura de 50.000 kg de 25/09/2026 a 30/09/2026, coberta pelo recebimento',mc)
    clk('Enviar para cotação'); tl=T(); nav('Abrir Compra de insumos ›','CMP.dc.html')
    fz2=J("[...document.querySelectorAll('span')].filter(s=>s.children.length===0&&/^Fazenda /.test(s.innerText.trim())).map(s=>s.innerText.trim())")
    etapa(3); cg=[rowtxt('Corretivos'),rowtxt('Mudas')]; clk('Enviar convites (simulado)'); tc=T(); time.sleep(3.5); trl=trail(); foto('8_cmp_lg_etapa3')
    chk('30 Compra da SOL-2026-09: Fazenda Lagoa Grande; Corretivos e Mudas "Sem fornecedor homologado" com link de cadastro; convites dos outros grupos saem e as propostas chegam',
        tl.startswith('Solicitação SOL-2026-09 enviada a Compras: 12 insumos') and fz2==['Fazenda Lagoa Grande'] and all('Sem fornecedor homologado' in x and 'Cadastrar em Parceiros e fornecedores' in x for x in cg)
        and tc.startswith('Convites simulados') and tc.endswith('Sem cotação (sem fornecedor homologado): Corretivos, Mudas.') and 'convites enviados' in trl and ' 0 propostas' not in trl,(tl,fz2,cg,tc,trl))
    # ---------------- bordas de endereço ----------------
    ir('CMP.dc.html#sol=SOL-9999&saf=S27SF',w=1.4); b1=(url(),cur(),T())
    ir('CMP.dc.html#saf=S2526',w=1.4); b2=(url(),cur(),T())
    chk('31 endereço com SOL de outra safra abre a SOL da safra e corrige o endereço; safra encerrada por endereço abre a consulta (etapa 6)',
        b1[0]=='/CMP.dc.html#sol=SOL-2027-02&saf=S27SF' and b1[1].startswith('2 ') and b1[2]=='SOL-9999 não é a solicitação da Safrinha 2027: aberta a SOL-2027-02.'
        and b2[1].startswith('6 ') and 'encerrada' in b2[2] and 'não está gravada' not in b2[2],(b1,b2))
    c.size(390,844); ir('CMP.dc.html#sol=SOL-2027-02&saf=S27SF',w=1.4); foto('6_cmp_390'); col()
    chk('22 sem erro JS (ouvinte de error e unhandledrejection em cada página aberta)', ERR==[], ERR[:5])
finally:
    c.close(); srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)
