# -*- coding: utf-8 -*-
"""Teste CDP · QUALIDADE-ARTEFATO-20261003-FLUXO item 1 (continuidade SAF → CMP) e item 2 (CAL-01 na tela).
Safrinha 2027 → etapa 4 (demanda de insumos; era a 6 até 05/10/2026) → Enviar para cotação gera SOL-2027-02 com o registro único (talhao-os-compras-v1: ID, fazenda, safra, itens,
estado e origem) → Abrir Compra de insumos abre a MESMA solicitação (CMP.dc.html#sol=…&saf=…) na etapa 2 com os mesmos itens, valor e
memória CAL-01 → recarregar mantém → Ver origem volta ao Planejar safra na demanda de insumos (passo=demanda). Cada safra guarda o próprio andamento da compra, que
sobrevive à ida e volta (registro proc) e aparece no Planejar safra. Lagoa Grande: realizado fora da demanda, fazenda certa, grupos sem
homologado não travam os convites. Paridade da tela (safra.js) com dados2.demanda e bordas de endereço. Erros JS por ouvinte próprio.
Uso: python3 saf_cmp_continuidade_test.py [pasta_png]   (≈ 100 s; capturas q_saf-cmp_*.png em _probe/)"""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
from comp_lib import cv_todas_sempre
R=os.path.join(HERE,'_render'); OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_probe'); os.makedirs(OUT,exist_ok=True)
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
OK=[]; FAIL=[]
def chk(nome,cond,det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ')+nome+('' if cond else f' · {str(det)[:400]}'),flush=True)
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
c=Chrome(port=free()); J=c.js; B=f'http://127.0.0.1:{p}/'; cv_todas_sempre(c)   # VISOES-2 §3.6 / SAF-TAB: o teste lê colunas fora do padrão
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
    # TAB-05 no motor (DS-MODULOS-2, 17/10/2026): as ações da linha ("Abrir compra", "Continuar…") moram no ⋯ da própria linha; o texto da linha
    # termina com os itens desse ⋯
    rowtxt=lambda t: J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].filter(x=>x.offsetParent).find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(t)})>=0); if(!r) return 'sem linha'; const m=[...r.querySelectorAll('.g2mais-menu [role=menuitem]')].map(i=>i.textContent.trim()).filter(Boolean).join(' '); return (r.innerText+(m?' '+m:'')).replace(/\\s+/g,' ');}})()") or ''
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
    # ---------------- Planejar safra · Safrinha 2027 · etapa 4 (demanda de insumos) ----------------
    r=J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safrinha 2027')>=0); const b=r&&[...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())); if(!b) return 'sem botão'; b.click(); return b.innerText.trim();})()"""); time.sleep(.6)
    chk('1 SAF: Safrinha 2027 abre direto na etapa 4, demanda de insumos ("Continuar: enviar demanda para cotação")',r=='Continuar: enviar demanda para cotação' and cur().startswith('4 '),(r,cur()))
    k6=J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]")
    # CTL-4 (demanda única): as O.S. abertas entram na demanda da fazenda e a parte do plano que elas cobrem sai (antes R$ 1.098.502,50);
    # o valor sai da quantidade a comprar com 0,01 da unidade, a mesma da Compra (Fungicida A 22,98 L: R$ 1.094.947,10, nunca 1.094.946,91 aqui e 947,10 lá)
    chk('2 SAF demanda de insumos (CAL-01): R$ 1.094.947,10 · 8 insumos a comprar · ainda não enviada',k6=='Valor da necessidade líquida R$ 1.094.947,10 · 8 insumos a comprar · ainda não enviada',k6)
    clk('Expandir tudo'); mp=rowtxt('MAP 11-52')
    # TABELAS-FOCO (5983172395): necessidade, unidade, data da falta e "usado antes" em colunas próprias
    # a unidade fica junto do valor (decisão do proprietário, 05/10/2026); data da falta e "usado antes" em colunas próprias
    mpc=[cel('MAP 11-52',k) for k in ('Necessidade líquida','Falta em','Usado antes da compra')]
    # revisão do 853a6a8 (achado 1): os 500 kg em custódia sem uso da OS-0417 (em conferência) são suprimento da fazenda e a Safra 2026/27 os usa antes
    chk('3 SAF MAP 11-52: 101.440 kg com falta em 20/02/2027 · estoque apto 90.000 + 500 em custódia usados antes',mpc==['101.440 kg','20/02/2027','90.500 kg'],(mpc,mp))
    rowclick('MAP 11-52'); m_saf=memo(); fechar()
    chk('4 SAF memória MAP: estoque apto, usos da Safra 2026/27 antes, resultado com a data',m_saf[:1]==['Estoque apto hoje: 90.000 kg + 500 kg em custódia sem uso nas O.S., a devolver ao Estoque (500 kg · REQ-031 · OS-0417 (em conferência)) = 90.500 kg'] and any(l.startswith('15/10/2026 · Safra 2026/27 · 1 uso · −') for l in m_saf)
        and m_saf[-1]=='Necessidade líquida = soma das faltas desta safra = 101.440 kg · falta a partir de 20/02/2027',m_saf)
    foto('1_saf_etapa6')
    clk('Enviar para cotação'); t=T()
    chk('5 SAF envia SOL-2027-02: 8 insumos, R$ 1.094.947,10, origem Safrinha 2027 · demanda de insumos',t.startswith('Solicitação SOL-2027-02 enviada a Compras: 8 insumos, R$ 1.094.947,10. Origem: Safrinha 2027 · Planejar safra, demanda de insumos.'),t)
    g=ls(); s=((g or {}).get('sols') or {}).get('S27SF') or {}
    chk('6 registro único talhao-os-compras-v1: ID, fazenda, safra, 8 itens, estado e origem',s.get('id')=='SOL-2027-02' and s.get('safra')=='S27SF' and s.get('nome')=='Safrinha 2027' and s.get('faz')=='Santa Rita'
        and len(s.get('itens') or {})==8 and s.get('estado')=='Enviada · a cotar' and (s.get('origem') or {}).get('h')=='SAF.dc.html#saf=S27SF&passo=demanda' and abs((s.get('total') or 0)-1094947.10)<0.01,
        {k:s.get(k) for k in ['id','safra','nome','faz','estado','origem','total']})
    clk('Enviar para cotação') if J("[...document.querySelectorAll('button')].some(b=>b.offsetParent&&b.innerText.trim()==='Enviar para cotação')") else None
    chk('7 SAF: tudo enviado, a ação principal vira "Abrir Compra de insumos ›" (sem duplicar)',J("[...document.querySelectorAll('button,a')].filter(b=>b.offsetParent).some(b=>b.innerText.trim()==='Abrir Compra de insumos ›')") and len((ls() or {}).get('sols',{}))==1)
    foto('2_saf_enviado')
    # ---------------- Compra de insumos · a mesma solicitação ----------------
    nav('Abrir Compra de insumos ›','CMP.dc.html')
    chk('8 CMP abre a mesma solicitação: #sol=SOL-2027-02&saf=S27SF, etapa 2, contexto "Safrinha 2027 · SOL-2027-02"',url()=='/CMP.dc.html#sol=SOL-2027-02&saf=S27SF' and cur().startswith('2 Confira a demanda') and 'Safrinha 2027 · SOL-2027-02' in body(),(url(),cur()))
    k2=J("(document.body.innerText.match(/SOL-2027-02 · Safrinha 2027[^\\n]+/)||[''])[0]"); tot=J("[...document.querySelectorAll('.g2tot')].filter(x=>x.offsetParent).map(x=>x.innerText).join(' ')") or ''
    chk('9 CMP etapa 2: mesmos 8 insumos e R$ 1.094.947,10 (resumo e total da tabela)','8 insumos a comprar · R$ 1.094.947,10 a preço de referência' in k2 and '1.094.947,10' in tot,(k2,tot))
    clk('Expandir tudo'); mp2=rowtxt('MAP 11-52')
    chk('10 CMP MAP 11-52: 101.440 · falta a partir de 20/02/2027 · estoque usado antes: 90.500 (com os 500 kg em custódia da OS-0417)',all(x in mp2 for x in ['101.440','20/02/2027','usado antes: 90.500']),mp2)
    rowclick('MAP 11-52'); m_cmp=memo(); lk=J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>[a.innerText.trim(),a.getAttribute('href')])") or []; foto('3b_cmp_memoria_cal01'); fechar()
    chk('11 mesma memória CAL-01 nas duas telas (MAP 11-52, linha a linha)',m_cmp==m_saf and len(m_saf)>=6,{'saf':m_saf,'cmp':m_cmp})
    chk('12 origem do insumo volta ao Planejar safra na demanda de insumos da Safrinha (passo=demanda)',any(t.startswith('Ver no Planejar safra · demanda de insumos') and h=='SAF.dc.html#saf=S27SF&passo=demanda' for t,h in lk),lk)
    foto('3_cmp_etapa2')
    ir('CMP.dc.html#sol=SOL-2027-02&saf=S27SF',w=1.4)
    chk('13 recarregar a Compra mantém SOL-2027-02 na etapa 2',cur().startswith('2 Confira a demanda') and 'Safrinha 2027 · SOL-2027-02' in body() and '1.094.947,10' in body(),(cur(),url()))
    etapa(1); sf=rowtxt('Safrinha 2027'); s7=rowtxt('Safra 2026/27')
    chk('14 CMP etapa 1: Safrinha com SOL-2027-02 · 8 insumos · R$ 1.094.947,10 · A cotar; 2026/27 continua SOL-2026-07 · R$ 428.305,00',
        all(x in sf for x in ['SOL-2027-02','8 insumos · R$ 1.094.947,10','A cotar','Abrir compra']) and 'Sem solicitação' not in sf and 'SOL-2026-07' in s7 and 'R$ 428.305,00' in s7,(sf,s7))
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
    h=J("(()=>{const a=[...document.querySelectorAll('a')].find(a=>a.offsetParent&&a.innerText.trim()==='Ver origem · demanda de insumos ›'); return a?a.getAttribute('href'):'';})()")
    chk('18 trilha da compra oferece "Ver origem · demanda de insumos ›" para a Safrinha',h=='SAF.dc.html#saf=S27SF&passo=demanda',h)
    tr0=trail(); nav('Ver origem · demanda de insumos ›','SAF.dc.html')
    k6b=J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]")
    chk('19 SAF volta na demanda de insumos (etapa 4) da Safrinha e mostra o andamento da compra (registro proc): SOL-2027-02 · Em cotação · N de 13 respostas',cur().startswith('4 ') and 'Safrinha 2027' in J("document.body.innerText.slice(0,600)") and 'solicitação SOL-2027-02 · Em cotação · ' in k6b and 'de 13 respostas' in k6b,(cur(),k6b))
    foto('5_saf_volta')
    nav('Abrir Compra de insumos ›','CMP.dc.html'); tr1=trail(); g=ls() or {}
    chk('26 Compra → origem → Compra: convites e propostas da SOL-2027-02 continuam (trilha igual) e o registro guarda o estado',
        '13 convites enviados' in tr1 and ' 0 propostas' not in tr1 and tr1==tr0 and (g.get('proc') or {}).get('S27SF',{}).get('estado','').startswith('Em cotação') and (g.get('sols') or {}).get('S27SF',{}).get('estado','').startswith('Em cotação'),
        {'antes':tr0,'depois':tr1,'proc':(g.get('proc') or {}).get('S27SF',{}).get('estado'),'sol':(g.get('sols') or {}).get('S27SF',{}).get('estado')})
    ir('SAF.dc.html'); px=rowtxt('Safrinha 2027')
    chk('20 SAF recarregada sem endereço: a Safrinha não volta a "enviar demanda" (registro mantido)','enviar demanda' not in px and 'Continuar' in px,px)
    # ---------------- mesma memória na Safra 2026/27 (reserva de outro destino) ----------------
    J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('Safra 2026/27')>=0); [...r.querySelectorAll('button')].find(b=>/^Continuar/.test(b.innerText.trim())).click();})()"""); time.sleep(.5)
    etapa(4); w=J("(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const box=t.parentElement; return {box:box.clientWidth, scroll:box.scrollWidth, tab:Math.round(t.getBoundingClientRect().width)};})()")
    hs=J("[...[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent).querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' ').replace(/ ⇅.*$/,'').trim())") or []
    # TABELAS-FOCO item 6: com uma variável por coluna a tabela pode rolar dentro da caixa; a página não rola e "1º uso" segue logo depois do insumo (v3.8)
    pg=J("[document.documentElement.scrollWidth, innerWidth]")
    # com a rolagem no início, as colunas essenciais da compra ficam à vista dentro da caixa (não basta a página não rolar)
    vis=J("""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const box=t.parentElement; box.scrollLeft=0; const R=box.getBoundingClientRect();
      return [...t.querySelectorAll('[role=columnheader]')].filter(h=>R.right+0.5>=h.getBoundingClientRect().right).map(h=>h.innerText.replace(/[⇅▾▴]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());})()""") or []
    ess=['GRUPO','INSUMO','1º USO','NECESSIDADE LÍQUIDA','FALTA EM']
    chk('23 SAF demanda de insumos, etapa 4 (2026/27, grupos recolhidos): a página não rola; "1º uso" logo depois de Grupo | Insumo (v3.8); Necessidade líquida e Falta em à vista sem rolar a tabela',
        pg[0]<=pg[1]+1 and len(hs)>3 and [h.upper() for h in hs[:3]]==['GRUPO','INSUMO','1º USO'] and all(x in vis for x in ess),(w,pg,hs[:4],vis))
    clk('Expandir tudo'); fa=rowtxt('Fungicida A'); gl=rowtxt('Glifosato 480'); rowclick('Glifosato 480'); gm=memo(); fechar()
    # CTL-4 (DEM-01/02): a OS-0430 (A liberar, chave c1|a1, T1-A) cobre a dessecação do T1-A: o uso entra pela ordem, com a mesma conta
    chk('24 memória como extrato por data, com a origem: "25/09/2026 · T1-A · OS-0430 · Dessecação pré-plantio · 2,00 L/ha × 160 ha = 320,0 L"; 1º uso intacto',
        any(l.startswith('25/09/2026 · T1-A · OS-0430 · Dessecação pré-plantio · 2,00 L/ha × 160 ha = 320,0 L → saldo') for l in gm) and cel('Glifosato 480','1º uso')=='25/09/2026',(gl,gm[:3]))
    rowclick('Fungicida A'); fs=memo(); fechar(); fa=fa+' | '+' · '.join(cel('Fungicida A',k) for k in ('Estoque apto','Usado antes da compra','Necessidade líquida'))
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627',w=1.4); clk('Expandir tudo'); fa2=rowtxt('Fungicida A'); rowclick('Fungicida A'); fc=memo(); fechar()
    sol7=list(D2.sol_itens())
    # CTL-4 (DEM-01/02/04): a OS-0421 cobre a 1ª aplicação (350 de 610 ha) e conta pelo pendente (15 L); a reserva da OS-0424 conta uma vez com a ordem.
    # Antes: 145,2 L a comprar (compra em dobro do que a OS-0421 já tem). Fungicida A e Adjuvante saem da SOL-2026-07.
    chk('21 Fungicida A (2026/27): estoque apto 545 L (65 reservados à OS-0424, a mesma demanda) · 0 L a comprar (nunca 145,2 L); memória com a OS-0421 pelo pendente e a reserva contada uma vez, igual nas duas telas; Fungicida A e Adjuvante fora da SOL-2026-07',
        fa.endswith(' | 545,0 L · — · 0,0 L') and 'res. 65,0' in fa2 and '145,2' not in fa2 and fs==fc
        and '23/09/2026 · T1+T2 · OS-0421 · Fungicida 1ª aplicação · 0,50 L/ha × 160 ha − 65 L em custódia = 15,0 L → saldo 530 L' in fs
        and '24/09/2026 · Reserva REQ-039 · OS-0424 (T1-B) · 65,0 L da mesma demanda, contados uma vez' in fs
        and any(l.startswith('29/11/2026 · T1-A · Fungicida 1ª aplicação · parte sem O.S. (OS-0421 cobre 350 de 610 ha, rateados pela área) · 0,50 L/ha × 68,2 ha = 34,1 L') for l in fs)
        and not ({'Fungicida A','Adjuvante espalhante'} & set(sol7)),{'fa':fa,'fa2':fa2,'iguais':fs==fc,'saf':fs[:4],'cmp':fc[-2:],'sol':sol7})
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
    chk('27 paridade na tela: demanda de insumos (endereço antigo etapa=6) de S2627, S27SF e LG2627 = dados2.demanda (valor e nº de insumos)',all(x[1] for x in par),par)
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
    chk(f"28 SAF Mamão 2026/27: Fazenda Lagoa Grande; nenhuma falta antes de hoje; calcário com {nk(cdm['real'])} kg antes de hoje sem O.S. (coluna 'Antes de hoje sem O.S.', DEM-06), {rup_} coberta pelo recebimento, 0 a comprar (= dados2.demanda)",
        fz==['Fazenda Lagoa Grande'] and not passadas and cdm['liq']==0 and cdm['rup']>0
        and [cel('Calcário dolomítico filler',k) for k in ('Antes de hoje sem O.S.','Falta em','Coberta em','Situação','Demanda bruta')]==[nk(cdm['real'])+' kg',dm_(cdm['falta'])+'/'+cdm['falta'][:4],dm_(cdm['cob'])+'/'+cdm['cob'][:4],'Coberto pelo recebimento',nk(cdm['bruta'])+' kg'],
        (fz,passadas,cal,[cel('Calcário dolomítico filler',k) for k in ('Antes de hoje sem O.S.','Falta em','Coberta em','Situação','Demanda bruta')]))
    rowclick('Calcário dolomítico filler'); mc=memo(); fechar(); foto('7_saf_lg_etapa6')
    chk('29 memória do calcário: antes de hoje sem O.S. fora da demanda (histórico do plano, nunca "Realizado"), ruptura na calagem de 25/09, recebimento de 30/09 cobre, sem compra nova',
        len(mc)>2 and mc[1].startswith('Antes de 23/09/2026 sem O.S. · ') and not any(l.startswith('Realizado') for l in mc) and any(l.startswith('30/09/2026 · ') and l.endswith('cobre a ruptura') for l in mc)
        and mc[-1]==f"Sem compra nova · ruptura de {nk(cdm['rup'])} kg de {dm_(cdm['falta'])}/{cdm['falta'][:4]} a {dm_(cdm['cob'])}/{cdm['cob'][:4]}, coberta pelo recebimento"
        and calagem_ok(mc),mc)
    clk('Enviar para cotação'); tl=T(); nav('Abrir Compra de insumos ›','CMP.dc.html')
    fz2=J("[...document.querySelectorAll('span')].filter(s=>s.children.length===0&&/^Fazenda /.test(s.innerText.trim())).map(s=>s.innerText.trim())")
    etapa(3); cg=[rowtxt('Corretivos'),rowtxt('Mudas')]; clk('Enviar convites (simulado)'); tc=T(); time.sleep(3.5); trl=trail(); foto('8_cmp_lg_etapa3')
    chk('30 Compra da SOL-2026-09: Fazenda Lagoa Grande; Corretivos e Mudas "Sem fornecedor homologado" com link de cadastro; convites dos outros grupos saem e as propostas chegam',
        tl.startswith('Solicitação SOL-2026-09 enviada a Compras: 13 insumos') and fz2==['Fazenda Lagoa Grande'] and all('Sem fornecedor homologado' in x and 'Cadastrar em Parceiros e fornecedores' in x for x in cg)
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
