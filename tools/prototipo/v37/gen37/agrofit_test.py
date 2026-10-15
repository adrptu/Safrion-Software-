# -*- coding: utf-8 -*-
"""Teste CDP (18 verificações) da AG-07 · Consulta Agrofit sobre a BASE REAL (dados abertos AGROFIT/MAPA, 02/10/2026).
Os esperados saem dos próprios arquivos servidos (agrofit_meta.json, agrofit_indice.json, agrofit_usos_cultura_*.json,
agrofit_lmr.json), da base da fazenda embutida na página (AGF) e do cenário compartilhado (window.__cen na O.S.), recalculados
aqui em Python com a mesma regra da página — nenhum número escrito à mão. Capturas em _probe/agrofit_real_*.png (1440×900).
CTL-5 (06/10/2026, RL-E3): a AG-07 só consulta; os itens 9, 12, 14 e 15 trocaram o receituário paralelo pelo "Usar na O.S."
(o registro nasce na O.S.; o fluxo inteiro está em ctl5_test.py). Praga-alvo (09/10/2026): com a cultura escolhida a lista é por uso
(produto × praga-alvo), e os itens 6 e 7 contam usos (o fluxo está em praga_alvo_test.py). Uso: python3 agrofit_test.py (≈ 40 s)."""
import sys, os, time, subprocess, json, unicodedata
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import Chrome
from journeys import free
R=os.path.join(HERE,'_render'); PROBE=os.path.join(HERE,'_probe'); os.makedirs(PROBE,exist_ok=True); p=free()
OFICIAL='https://agrofit.agricultura.gov.br/agrofit_cons/principal_agrofit_cons'
ACC='rgb(30, 122, 76)'
ld=lambda f: json.load(open(os.path.join(R,f),encoding='utf-8'))
META=ld('agrofit_meta.json'); IDX=ld('agrofit_indice.json'); LMR=ld('agrofit_lmr.json')
U={}
for i in range(META['contagens']['fatias_cultura']): U.update(ld(f'agrofit_usos_cultura_{i}.json')['culturas'])
_s=open(os.path.join(R,'AG-07.dc.html'),encoding='utf-8').read()
AGF,_=json.JSONDecoder().raw_decode(_s,_s.index('AGF = ')+6)
REF={r['id']:r for r in AGF['ref']}
def nz(t): return ''.join(ch for ch in unicodedata.normalize('NFD',str(t)) if not ('̀'<=ch<='ͯ')).lower()
def nf(n,d=2):   # número pt-BR (milhar com ponto)
    s=f'{float(n):,.{d}f}'.rstrip('0').rstrip('.') if d else f'{float(n):,.0f}'; return s.replace(',','X').replace('.',',').replace('X','.')
# ---------- a base, com a mesma regra da página ----------
F={c:i for i,c in enumerate(IDX['campos'])}; IG=IDX['ingredientes']; GQ=IDX['gruposQuimicos']; CL=IDX['classes']; CU=IDX['culturas']; TD=IDX['todasCulturas']
def casa(n,pt): return n==pt or (n.startswith(pt) and not (n[len(pt):len(pt)+1].isalnum() and n[len(pt):len(pt)+1].isascii()))
REFC=[[c for pts,c in AGF['grupo_ref'] if any(casa(nz(x[0]).strip(),pt) for pt in pts)] for x in IG]
GEN={nz(g).strip() for g in AGF['gq_gen']}; GNOME={k:v[0] for k,v in AGF['grupos'].items()}
import re as _re
def rotk(ids):   # = agRotKeys da página: s = sítio específico, m = multissítio (FRAC M); UN não une
    s=set(); m=set()
    for k in ids:
        cs=[c for c in REFC[k] if not _re.search(r'\bUN|N-UN',c)]
        if cs:
            for c in cs: (m if c.startswith('FRAC M') else s).add('c'+c)
            continue
        g=IG[k][1]; s.add(('q%d'%g) if g is not None and nz(GQ[g]).strip() not in GEN else ('i%d'%k))
    return s,m
def mesmo(p,q):  # = agMesmo da página
    (ps,pm),(qs,qm)=p['rot'],q['rot']
    if qs&ps: return True
    if not qs: return bool(qm&pm) if not ps else (bool(qm) and qm<=pm)
    return False
P=[]
for i,r in enumerate(IDX['produtos']):
    ids=[x[0] for x in r[F['ingredientes']]]; cls=r[F['classes']]; gq=[]
    for g in (IG[k][1] for k in ids):
        if g is not None and g not in gq: gq.append(g)
    codes=sorted({c for k in ids for c in REFC[k]},key=lambda c:(c.split()[0],[(0,int(t)) if t.isdigit() else (1,t) for t in _re.findall(r'\d+|\D+',c.split(' ',1)[1])])); fo=IDX['formulacoes'][r[F['formulacao']]]
    modo=IDX['modos'][r[F['modo']]] if r[F['modo']] is not None and r[F['modo']]>=0 else ''
    comp=list(dict.fromkeys(CL[c][1] for c in cls)); bio=any(CL[c][2]==1 for c in cls)
    x=dict(i=i,reg=str(r[F['registro']]),nome=(r[F['marcas']] or ['Registro '+str(r[F['registro']])])[0],ids=ids,key=','.join(map(str,sorted(ids))),
           cul=set(r[F['culturas']]),comp=comp,org=r[F['organico']],ing=r[F['ingredientes']],tit=IDX['titulares'][r[F['titular']]],
           rot=rotk(ids),codes=codes,gqT=' + '.join(GQ[g] for g in gq))
    x['moa']=(' + '.join(codes)+' · '+' + '.join(GNOME.get(k,k) for k in codes)) if codes else ((x['gqT'] or 'grupo químico não informado')+' · sem código de referência')
    conc=' + '.join(str(i[1]) for i in r[F['ingredientes']] if i[1] is not None)   # a página procura também pela concentração (15/10/2026)
    x['hay']=nz(' '.join([x['reg'],' '.join(r[F['marcas']]),' + '.join(IG[k][0] for k in ids),conc,' + '.join(GQ[g] for g in gq),' + '.join(codes),' + '.join(GNOME.get(k,k) for k in codes),x['tit'],
                          ', '.join(dict.fromkeys(CL[c][0] for c in cls)),' '.join(comp),'biologico' if bio else '',modo,fo[0],fo[1]]))
    P.append(x)
REG={x['reg']:x for x in P}
PAIRS=[(int(c),a,ps) for c,L in U.items() for a,ps in L]
def cid(nome): return next(i for i,c in enumerate(CU) if c[0]==nome)
def aid(sci): return next(i for i,a in enumerate(IDX['alvos']) if a[0]==sci)
def busca(q,cul=None):
    ws=nz(q).split(); ALL=(1<<len(ws))-1; ok=set(); pm={}
    for x in P:
        if cul is not None and not (cul in x['cul'] or TD in x['cul']): continue
        m=sum(1<<b for b,w in enumerate(ws) if w in x['hay'])
        if m==ALL: ok.add(x['i'])
        else: pm[x['i']]=m
    for c,a,ps in PAIRS:
        if cul is not None and c not in (cul,TD): continue
        al=IDX['alvos'][a]; h=nz(CU[c][0]+' '+al[0]+' '+' '.join(al[1] or []))
        m=sum(1<<b for b,w in enumerate(ws) if w in h)
        if m: ok.update(i for i in ps if i in pm and (pm[i]|m)==ALL)
    return ok
def usos(c,a): return set(dict(U.get(str(c),[])).get(a,[]))
NOMEID={nz(g[0]).strip():i for i,g in enumerate(IG)}
def gk(r): return ','.join(map(str,sorted(NOMEID[nz(n).strip()] for n in r['agrofit']))) if r['agrofit'] else None   # chave da ficha da fazenda
DT='02/10/2026' if META['fontes']['formulados']['last_modified'].startswith('Fri, 02 Oct 2026') else None
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=None; OK=[]; FAIL=[]; ERRS=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,('' if cond else str(info)[:900]),flush=True)
t0=time.time()
try:
    c=Chrome(port=free()); J=c.js; c.size(1440,900)
    c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));const __ce=console.error;console.error=function(){window.__errs.push([...arguments].map(String).join(' ').slice(0,300));__ce.apply(console,arguments);};"
        # falha simulada do índice (só quando a página pede: ?falha=1) para conferir o estado de erro e o "Tentar de novo"
        "if(location.search.indexOf('falha=1')>=0){ window.__agFail=true; const f0=window.fetch; window.fetch=function(u,o){ if(window.__agFail&&String(u).indexOf('agrofit_indice')>=0) return Promise.reject(new Error('rede indisponível (simulada)')); return f0.apply(this,arguments); }; }"})
    def junta(pag): ERRS.extend(f'{pag}: {e}' for e in (J("(window.__errs||[]).filter(e=>e.indexOf(\"reading 'g2toast'\")<0)") or []))
    U_=lambda f: f'http://127.0.0.1:{p}/{f}'
    J0="window.__setv=(sel,val)=>{const el=document.querySelector(sel); if(!el) return 'SEM '+sel; const pr=el.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(pr,'value').set.call(el,val); el.dispatchEvent(new Event(el.tagName==='SELECT'?'change':'input',{bubbles:true})); return 'ok';}; 1"
    setv=lambda sel,val: (J(f"__setv({json.dumps(sel)},{json.dumps(val)})"),time.sleep(.35))[0]
    cnt=lambda: J("(()=>{const s=[...document.querySelectorAll('main span')].find(x=>/ de [\\d.]+ (produtos|usos em .+)$/.test(x.innerText.trim())); return s?s.innerText.trim():'';})()") or ''
    rows=lambda: J("[...document.querySelectorAll('main [role=table] [role=row].g2ed')].map(r=>[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.trim()))") or []
    status=lambda: J("[...document.querySelectorAll('main [role=status]')].map(x=>x.innerText.replace(/\\s+/g,' ').trim())") or []
    FX='aside[aria-label^="Ficha"]'; RX='aside[aria-label="Preparar receituário agronômico"]'   # RX: a gaveta que saiu (CTL-5); só para conferir que não existe
    PASSO=lambda: J(f"(document.querySelector('{FX} [role=region][aria-label=\"Próximo passo\"]')||{{innerText:''}}).innerText.replace(/\\s+/g,' ')") or ''
    USAR=lambda: J(f"(()=>{{const b=[...document.querySelectorAll('{FX} button')].find(x=>x.innerText.trim()==='Usar na O.S.'); return b?b.disabled:null;}})()")
    ORDS=lambda: [o for o in (J(f"[...document.querySelectorAll('{FX} select[aria-label=\"Ordem A liberar\"] option')].map(o=>o.value)") or []) if o]
    ficha=lambda: J(f"(document.querySelector('{FX}')||{{}}).innerText||''") or ''
    clica=lambda raiz,txt: J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps(raiz+' button')})].find(x=>x.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(txt)})); if(!b) return 'NÃO ACHEI'; b.click(); return 'ok';}})()")
    def pronto(t=25):
        for _ in range(int(t/0.25)):
            if cnt() and J("document.body.innerText.indexOf('Carregando culturas e alvos')<0"): J(J0); return True
            time.sleep(.25)
        J(J0); return False
    def combo(rot, txt):   # Cultura e Praga-alvo são listas de escolha (13/10: um campo de busca por tela): a 1ª opção que começa com o texto (ou o contém)
        r = J(f"""(()=>{{const s=document.querySelector('select[aria-label={json.dumps(rot)}]'); if(!s) return 'sem lista';
          const n=x=>String(x||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim(); const q=n({json.dumps(txt)}); const os=[...s.options];
          const o=q===''?os.find(o=>o.value===''):(os.find(o=>o.value!==''&&n(o.text).startsWith(q))||os.find(o=>o.value!==''&&n(o.text).indexOf(q)>=0));
          if(!o) return 'sem opção'; s.value=o.value; s.dispatchEvent(new Event('change',{{bubbles:true}})); return 'ok';}})()"""); time.sleep(.4)
        return r
    shot=lambda n: c.shot(os.path.join(PROBE,f'agrofit_real_{n}.png'))
    # navegação sem submenus (13/10/2026, ui37.MENU2/HUB37/CURTO37/VOLTA37): módulo marcado, "‹ Módulo" e os cartões da tela de entrada
    NAV="JSON.stringify((()=>{const n=document.querySelector('nav[aria-label=Menu]'); const v=document.querySelector('a.volta37'); return {cur:n?[...n.querySelectorAll('a[aria-current=page]')].map(a=>a.getAttribute('aria-label')):[], volta:v?[v.getAttribute('href'),v.innerText.replace(/\\s+/g,' ').trim()]:null};})())"
    CARDS="JSON.stringify([...document.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length).map(a=>[a.getAttribute('href'),a.innerText.replace(/\\s+/g,' ').trim()]))"
    def espera(js,ate=20.0):   # condição observável (página nova pronta), não tempo fixo; no limite devolve False e a verificação falha
        t1=time.time()
        while time.time()-t1<ate:
            try:
                if J(js): return True
            except Exception: pass
            time.sleep(.1)
        return False

    # ---------- 1 · O.S.: menu e atalho "Agrofit ›" (links antigos #<id da ficha da fazenda>) ----------
    c.goto(U_('Main.dc.html'),wait=.8); J("localStorage.removeItem('talhao-os-cenario-v1')")
    c.goto(U_('OS.dc.html#OS-0430'),wait=1.5)
    cen=J("(()=>{const c=window.__cen.cenGet(); return {lotes:Object.values(c.lotes), ins430:c.ordens['OS-0430'].ins.map(x=>x.p)};})()")
    nv=json.loads(J(NAV) or '{}')
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(x=>x.innerText.trim()==='Ajustar antes de liberar'); if(b) b.click();})()"); time.sleep(.5)
    lk=J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ajustar antes de liberar\"]'); return g?[...g.querySelectorAll('a')].filter(a=>a.innerText.trim()==='Agrofit ›').map(a=>[a.getAttribute('href'),a.target,a.rel]):[];})()") or []
    esp=sorted('AG-07.dc.html#'+r['id'] for n in cen['ins430'] for r in AGF['ref'] if n in r['nomes_fazenda'])
    J("window.__cen.cenMudar(null,c=>({msg:''}))"); junta('OS')
    # Agrícola começa pela Consulta Agrofit: "‹ Agrícola" da O.S. → tela de entrada (antes: subitens do menu lateral). Desde 14/10/2026 a tela de
    # entrada é o fluxo do processo (ui37.FLUXO37, mod_fluxo_test.py): o Agrofit abre o 1º bloco, antes de Planos agronômicos; o Painel fecha o último
    J("(document.querySelector('a.volta37')||{click:()=>0}).click()"); hub=espera("location.pathname.endsWith('/MOD-AGR.dc.html') && document.readyState==='complete' && document.querySelectorAll('a.mod-cartao').length>0")
    m=json.loads(J(CARDS) or '[]'); junta('MOD-AGR')
    ix=lambda h: [x[0] for x in m].index(h) if h in [x[0] for x in m] else -1
    chk('1 O.S.: o fluxo do Agrícola começa pelo Agrofit, antes de Planos agronômicos (tela de entrada, aberta por "‹ Agrícola"); OS-0430 › Ajustar: "Agrofit ›" → AG-07.dc.html#<ficha>, nova aba',
        hub and nv.get('cur')==['Agrícola'] and nv.get('volta')==['MOD-AGR.dc.html','‹ Agrícola'] and m[:1]==[['AG-07.dc.html','Agrofit']] and 0<ix('PA.dc.html') and ix('PAGR.dc.html')==len(m)-1
        and esp and sorted(h for h,_,_ in lk)==esp and all(t=='_blank' and 'noopener' in (r or '') for _,t,r in lk), [nv,hub,m[:3],esp,lk])

    # ---------- 2 · o link antigo da O.S. abre a lista filtrada pelo mesmo ingrediente ----------
    alvo=esp[0]; r0=REF[alvo.split('#')[1]]; k0=gk(r0); L0=[x for x in P if x['key']==k0]; n0=len(L0)
    c.goto(U_(alvo),wait=1.0); pronto(); st=status()
    rg=J("(document.querySelector('main [role=region][aria-label=\"Referência conferida em bula\"]')||{}).innerText||''") or ''
    u0=r0['usos'][0]
    ok2=ficha().startswith(L0[0]['nome']) if n0==1 else \
        (cnt()==f'{nf(n0,0)} de {nf(len(P),0)} produtos' and any(s.startswith('Da fazenda: '+r0['nome']) and f'{nf(n0,0)} produtos registrados' in s for s in st)
         and r0['nome'] in rg and u0['dose'] in rg and u0['carencia'] in rg and all(a['texto'][:40] in rg for a in r0['alertas_fazenda']))
    chk(f'2 link da O.S. ({alvo}) abre algo útil: faixa "Da fazenda: {r0["nome"]}", a referência conferida (dose {u0["dose"]}, carência {u0["carencia"]}, alertas) já na chegada e os {n0} registros',ok2,[cnt(),st,rg[:300]])
    shot('ref_da_fazenda'); junta('AG-07 ref')

    # ---------- 3 · cabeçalho: selo, fonte e link oficial a partir da meta ----------
    c.goto(U_('AG-07.dc.html'),wait=.8); carregou=pronto()
    head=J("document.querySelector('header').innerText.replace(/\\n/g,' | ')") or ''
    ln=J("[...document.querySelectorAll('header a')].map(a=>[a.innerText.trim(),a.getAttribute('href'),a.target,a.rel])") or []
    NP=META['contagens']['registros']
    # o selo depende da idade do arquivo no relógio real (agDiasArq: mais de 7 dias = desatualizada); o oráculo calcula a idade aqui
    import email.utils, datetime as _dt
    IDADE=(_dt.datetime.now(_dt.timezone.utc)-email.utils.parsedate_to_datetime(META['fontes']['formulados']['last_modified'])).days
    SELO=f'Base de {DT} · desatualizada' if IDADE>7 else f'Base atualizada · {DT}'
    chk(f'3 cabeçalho: "{SELO}" (arquivo com {IDADE} dias) e "Fonte: AGROFIT/MAPA · dados abertos (CC-BY) · arquivo de {DT} · {nf(NP,0)} produtos com registro" + AGROFIT oficial (nova aba)',
        carregou and NP==len(P) and SELO in head and f'Fonte: AGROFIT/MAPA · dados abertos (CC-BY) · arquivo de {DT} · {nf(NP,0)} produtos com registro' in head
        and any(t.startswith('Abrir no AGROFIT oficial') and h==OFICIAL and tg=='_blank' and 'noopener' in (rl or '') for t,h,tg,rl in ln), [head,ln])
    # ---------- 4 · listagem: todos os registros, 7 colunas, render incremental ----------
    # (cdp.Chrome mostra todas as colunas, como quem escolheu "todas" no painel; o padrão sem Tox · amb, 15/10/2026, está em agrofit_faixa_test.py)
    cols=[nz(x).replace('⇅','').replace('▾','').strip() for x in (J("[...document.querySelectorAll('main [role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' '))") or [])]
    n50=len(rows()); clica('main','Mostrar mais'); time.sleep(.4); n150=len(rows())
    chk(f'4 lista: "{nf(NP,0)} de {nf(NP,0)} produtos", 7 colunas (com Alvos, 13/10), 50 linhas e "Mostrar mais" → 150',
        cnt()==f'{nf(NP,0)} de {nf(NP,0)} produtos' and n50==50 and n150==150
        and cols==['produto · registro','ingrediente ativo · grupo quimico','classe · modo de acao','culturas','alvos','tox · amb','na fazenda'], [cnt(),cols,n50,n150])
    shot('lista')
    # ---------- 5 · busca sem acento, cultura e alvo no MESMO uso ----------
    E5=busca('feijão percevejo'); setv('main input[type=search]','feijão percevejo'); a1=cnt(); setv('main input[type=search]','FEIJAO percevejo'); a2=cnt()
    sem=busca('soja percevejo')-E5   # tem percevejo na soja mas não no feijão: não pode aparecer
    nomes=set(r[0].split('\n')[0] for r in rows())
    chk(f'5 busca "feijão percevejo" = "FEIJAO percevejo" = {len(E5)} (cultura e alvo no mesmo uso; exclui quem só tem percevejo em outra cultura)',
        len(E5)>0 and a1==a2==f'{nf(len(E5),0)} de {nf(NP,0)} produtos' and not (nomes & {P[i]['nome'] for i in sem} - {P[i]['nome'] for i in E5}), [a1,a2,len(E5)])
    setv('main input[type=search]','')
    # ---------- 6 · Cultura = Soja (combobox) e "só os de Soja" ----------
    # Praga-alvo (09/10/2026): com a cultura escolhida a lista tem uma linha por USO na cultura (produto × praga-alvo); a contagem passou de
    # produtos a usos ("N de M usos em Soja") e "Ver só os de Soja" bate com nUsos da cultura no índice (antes: produtos, nProdutos)
    SJ=cid('Soja'); uS=sum(len(ps) for c_ in (SJ,TD) for a_,ps in U[str(c_)]); uSo=sum(len(ps) for a_,ps in U[str(SJ)])
    combo('Cultura','soja'); b1=cnt(); st=status(); clica('main','Ver só os de Soja'); b2=cnt()
    chk(f'6 Cultura Soja: {uS} usos (com "Todas as culturas") e "Ver só os de Soja" → {uSo} usos (= nUsos da cultura no índice)',
        b1==f'{nf(uS,0)} de {nf(uS,0)} usos em Soja' and b2==f'{nf(uSo,0)} de {nf(uSo,0)} usos em Soja' and uSo==CU[SJ][4]
        and any('Todas as culturas' in s for s in st), [b1,b2,st])
    clica('main','Incluir "Todas as culturas"')
    # ---------- 7 · Praga ou alvo (aparece com a cultura) ----------
    PH=aid('Phakopsora pachyrhizi'); eA=usos(SJ,PH)|usos(TD,PH)
    combo('Praga-alvo','phakopsora'); c7=cnt(); L7=rows(); vis7=set(r[0].split('\n')[0] for r in L7)
    chk(f'7 Praga ou alvo = Phakopsora pachyrhizi em Soja: {len(eA)} usos (Soja + "Todas as culturas"), linhas só deles, com o nome científico na coluna própria',
        c7==f'{nf(len(eA),0)} de {nf(uS,0)} usos em Soja' and vis7 and vis7<= {P[i]['nome'] for i in eA} and all(r[2]=='Phakopsora pachyrhizi' for r in L7), [c7,len(eA),L7[:2]])
    shot('soja_ferrugem')
    # ---------- 8 · Classe + agrupar por grupo químico ----------
    J("[...document.querySelectorAll('main button')].find(b=>/^Limpar filtros/.test(b.innerText.trim())).click()"); time.sleep(.4)
    setv('main [role=group][aria-label="Filtros"] select[aria-label="Classe"]','Herbicida'); c8=cnt()   # Classe na faixa "Filtros" (15/10/2026)
    HB=[x for x in P if 'Herbicida' in x['comp']]; GG={}
    for x in HB:
        gs=list(dict.fromkeys(IG[k][1] for k in x['ids'] if IG[k][1] is not None)) or [None]
        for g in gs: GG[GQ[g] if g is not None else '(grupo químico não informado)']=GG.get(GQ[g] if g is not None else '(grupo químico não informado)',0)+1
    setv('main select[aria-label="Agrupar por"]','gq')
    gr=J("[...document.querySelectorAll('main [role=table] [role=row].g2ed:not(.g2kid)')].map(r=>r.innerText.replace(/\\s+/g,' ').replace(/^[▾▸]\\s*/,'').trim())") or []
    mt=J("(()=>{const s=[...document.querySelectorAll('main span')].find(x=>/^Mostrando /.test(x.innerText)); return s?s.innerText:'';})()") or ''
    bate=all(any(t==f'{k} {nf(n,0)} produto{"s" if n>1 else ""}' for k,n in GG.items()) for t in gr)
    chk(f'8 Classe Herbicida = {len(HB)}; agrupar por grupo químico: {len(GG)} grupos, contagem de cada linha confere',
        c8==f'{nf(len(HB),0)} de {nf(NP,0)} produtos' and bate and len(gr)==min(50,len(GG)) and (len(GG)<=50 or f'de {nf(len(GG),0)} linhas' in mt), [c8,len(gr),len(GG),mt,gr[:3]])
    shot('agrupado_grupo_quimico')
    setv('main select[aria-label="Agrupar por"]',''); J("[...document.querySelectorAll('main button')].find(b=>/^Limpar filtros/.test(b.innerText.trim())).click()"); time.sleep(.3)
    junta('AG-07')

    # ---------- 9 · link novo #reg-<n>: ficha do registro, "Usar na O.S." desligado até cultura e alvo (CTL-5: antes "Preparar receituário") ----------
    S9=usos(SJ,PH); cand=[x for x in P if x['i'] in S9 and len(x['cul'])>=2 and len(x['ids'])>=2]
    X=cand[0]
    J(f"location.hash='#reg-{X['reg']}'"); time.sleep(.8); f=ficha()
    dis=USAR()
    lkf=J(f"[...document.querySelectorAll('{FX} a')].map(a=>[a.getAttribute('href'),a.target])") or []
    chk(f'9 #reg-{X["reg"]} abre a ficha de {X["nome"]}: registro, titular, 7 seções, link oficial, nota da bula e "Usar na O.S." desligado sem cultura/alvo',
        f.startswith(X['nome']) and f'Registro MAPA nº {X["reg"]} · {X["tit"]}' in f and dis is True and J("location.hash")=='#reg-'+X['reg']
        and all(s in nz(f) for s in ('usos registrados','rotacao','lmr anvisa','na fazenda','registro e composicao','dose, carencia'))
        and [OFICIAL,'_blank'] in lkf, [f[:300],dis,lkf])
    # ---------- 10 · rotação: mesma cultura × alvo, OUTRO MODO DE AÇÃO (código IRAC/FRAC/HRAC por ingrediente) ----------
    setv(f'{FX} select[aria-label="Cultura do uso"]',str(SJ)); setv(f'{FX} select[aria-label="Alvo do uso"]',str(PH)); f=ficha()
    cnd=(usos(SJ,PH)|usos(TD,PH))-{X['i']}; alt=[P[i] for i in cnd if not mesmo(X,P[i])]; nmes=len(cnd)-len(alt)
    ng=len({q['moa'] for q in alt})
    vist=J(f"[...document.querySelectorAll('{FX} [role=list][aria-label=\"Alternativas de outro modo de ação\"] button')].map(b=>b.innerText.replace(/ ›$/,'').trim())") or []
    okn={q['nome'] for q in alt}
    # invariante agronômica: nenhum alternativo repete um código de sítio específico do produto aberto (ex.: DMI → DMI)
    rep=[q['nome'] for q in alt if q['rot'][0] & X['rot'][0]]
    res=f'{nf(len(alt),0)} registros de outro modo de ação em {nf(ng,0)} grupos para Soja × '
    chk(f'10 rotação Soja × Phakopsora para {X["nome"]} ({" + ".join(X["codes"])}): {len(alt)} de outro modo de ação em {ng} grupos, {nmes} do mesmo; nenhum alternativo repete o modo de ação',
        res in f and f'{nf(nmes,0)} do mesmo modo de ação (não é rotação)' in f and vist and set(vist)<=okn and not rep, [res,nmes,vist[:6],rep[:4],f[f.find('ROTAÇÃO'):f.find('ROTAÇÃO')+300]])
    shot('ficha_rotacao')
    # ---------- 11 · LMR ANVISA da cultura escolhida ----------
    lm=J(f"[...document.querySelectorAll('{FX} [role=table][aria-label=\"LMR ANVISA\"] [role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' ').trim())") or []
    exp=[]
    for k in X['ids']:
        mono=LMR['monografias'].get(IG[k][2] or '',None); e=mono[2].get(CU[SJ][2]) if mono else None
        exp.append((IG[k][0], ('Valor 999' if e[0]>=999 else nf(e[0],4)+' mg/kg') if e and e[0] is not None else None))
    chk('11 LMR ANVISA para Soja: um valor por ingrediente, igual ao agrofit_lmr.json',
        len(lm)==len(exp) and all(l.startswith(n) and (v is None or v in l) for l,(n,v) in zip(lm,exp)), [lm,exp])
    # ---------- 12 · só consulta (CTL-5, RL-E3): sem gaveta de receituário; com cultura e alvo, o próximo passo é "Usar na O.S." ----------
    temF=bool(J(f"(()=>{{try{{const A=window.__agx.AGX; return !!A.FK[A.P[A.reg['{X['reg']}']].key];}}catch(e){{return null;}}}})()")); pa=PASSO(); fx=ficha()
    chk('12 só consulta: sem "Preparar receituário" nem "Receituário emitido"; Soja × alvo → "Usar na O.S." com as ordens A liberar de soja, ou desligado dizendo o motivo',
        not J(f"!!document.querySelector('{RX}')") and 'Preparar receituário' not in fx and 'Receituário emitido' not in fx
        and ((ORDS()==['OS-0430'] and ('Esta consulta não emite receituário' in pa or 'não está na referência conferida' in pa)) if temF else (USAR() is True and 'Sem produto da fazenda com este ingrediente ativo' in pa)), [temF,ORDS(),pa])   # revisão do CTL-5: só a ordem de pulverização (S3-1); alvo da referência (S3-3)
    junta('AG-07 ficha')

    # ---------- 13 · links antigos: filtro pelo ingrediente, registro único abre a ficha, proibido explica ----------
    from collections import Counter
    NK=Counter(x['key'] for x in P); nG=NK[gk(REF['glifosato-480'])]
    uni=[r for r in AGF['ref'] if r['agrofit'] and NK[gk(r)]==1]
    J("location.hash='#glifosato-480'"); time.sleep(.8); g1=cnt(); s1=status()
    J(f"location.hash='#{uni[0]['id']}'" if uni else "0"); time.sleep(.9); h2=J("location.hash"); f2=ficha()
    J("location.hash='#paraquate-200-sl'"); time.sleep(.8); g3=cnt(); s3=status()
    u0=next(x for x in P if x['key']==gk(uni[0])) if uni else {'reg':'?','nome':'?'}
    chk(f'13 links antigos: #glifosato-480 → {nG} registros; #{uni[0]["id"] if uni else "?"} (único) → ficha {u0["nome"]}; #paraquate-200-sl → 0 e "Proibido"',
        g1==f'{nf(nG,0)} de {nf(NP,0)} produtos' and any('Da fazenda: Glifosato 480' in s for s in s1) and h2=='#reg-'+u0['reg'] and f2.startswith(u0['nome'])
        and g3==f'0 de {nf(NP,0)} produtos' and any('Proibido' in s for s in s3), [g1,h2,f2[:40],g3,s3])
    # ---------- 14 · Na fazenda ao vivo (cenário) e referência conferida em bula (abamectina) ----------
    rA=REF['abamectina-18-ec']; kA=gk(rA); nfz=sorted({n for r in AGF['ref'] if gk(r)==kA for n in r['nomes_fazenda']})
    LA=sorted([l for l in cen['lotes'] if l['prod'] in nfz],key=lambda l:-max(0,(l['fisico'] or 0)-(l['quarentena'] or 0)-(l['reservado'] or 0)))
    XA=next(x for x in P if x['key']==kA and cid('Mamão') in x['cul'])
    J(f"location.hash='#reg-{XA['reg']}'"); time.sleep(.8); f=ficha()
    lot=J(f"[...document.querySelectorAll('{FX} [role=table][aria-label=\"Estoque por lote\"] [role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' ').trim())") or []
    disp=lambda l: max(0,(l['fisico'] or 0)-(l['quarentena'] or 0)-(l['reservado'] or 0))
    lin=[f"{l['prod']} {l['lote']} {l['local']} {nf(l['fisico'])} {l['un']} {nf(l['reservado'])} {l['un']} {nf(disp(l))} {l['un']}" for l in LA]
    MA=cid('Mamão'); alm=sorted(a for c_,a in ((c_,a) for c_,L in U.items() if int(c_)==MA for a,ps in L if XA['i'] in ps))
    setv(f'{FX} select[aria-label="Cultura do uso"]',str(MA)); setv(f'{FX} select[aria-label="Alvo do uso"]',str(alm[0]))
    pfs=J(f"!!document.querySelector('{FX} select[aria-label=\"Produto da fazenda\"]')"); d14=USAR()
    # dos 3 nomes da fazenda com abamectina, só a Abamectina 18 EC está no catálogo da O.S. (lote ou plano): é ela que vai, sem perguntar
    # revisão do CTL-5 (S3-1): só a ordem de pulverização do mamão (OS-0501) é candidata, e vem escolhida (lista de um item: um toque a menos)
    chk(f'14 Na fazenda ({XA["nome"]}): lotes de {", ".join(nfz)} iguais ao cenário; referência "Abamectina 18 EC"; Mamão: só a ordem de pulverização A liberar de mamão (OS-0501, já escolhida; o produto é o do catálogo da O.S.)',
        lot==lin and len(lin)>0 and 'REFERÊNCIA CONFERIDA EM BULA' in f.upper() and 'Abamectina 18 EC' in f
        and pfs is False and ORDS()==['OS-0501'], [lin,lot,pfs,d14,ORDS()])
    chk('14b com a ordem já escolhida, "Usar na O.S." liga e diz o próximo passo na OS-0501 com a Abamectina 18 EC para o ácaro da referência', d14 is False and USAR() is False
        and _re.search(r'Abre a OS-0501 em Ajustar antes de liberar com Abamectina 18 EC incluído para ácaro-(branco|rajado)\.', PASSO()), [d14,USAR(),PASSO()])
    J(f"(()=>{{const s=document.querySelector('{FX} section[aria-label=\"Na fazenda\"]'); if(s) s.scrollIntoView({{block:'start'}});}})()"); time.sleep(.3)
    shot('ficha_na_fazenda'); junta('AG-07 abamectina')

    # ---------- 15 · registro só em "Todas as culturas": a ficha oferece a cultura do talhão; "Usar na O.S." pede a cultura real (CTL-5) ----------
    XT=next(x for x in P if x['cul']=={TD} and 'Inseticida' in x['comp'])
    alT=sorted(a_ for a_,ps in U[str(TD)] if XT['i'] in ps)
    J(f"location.hash='#reg-{XT['reg']}'"); time.sleep(.8)
    op=J(f"[...document.querySelectorAll('{FX} select[aria-label=\"Cultura do uso\"] option')].map(o=>o.innerText)") or []
    setv(f'{FX} select[aria-label="Cultura do uso"]',str(TD))
    disTD=USAR(); dica=PASSO(); ordTD=ORDS()
    setv(f'{FX} select[aria-label="Cultura do uso"]',str(SJ)); setv(f'{FX} select[aria-label="Alvo do uso"]',str(alT[0])); time.sleep(.3)
    temT=bool(J(f"(()=>{{try{{const A=window.__agx.AGX; return !!A.FK[A.P[A.reg['{XT['reg']}']].key];}}catch(e){{return null;}}}})()")); pS=PASSO()
    chk(f'15 {XT["nome"]} (só "Todas as culturas"): Cultura oferece Soja; com "Todas as culturas" "Usar na O.S." fica desligado com orientação e sem ordens; com Soja vale a cultura real',
        'Soja · pelo uso em “Todas as culturas”' in op and disTD is True and 'escolha no campo Cultura a cultura do talhão' in dica and not ordTD
        and 'escolha no campo Cultura' not in pS and 'Receituário emitido' not in pS
        and ((ORDS()==['OS-0430']) if temT else ('Sem produto da fazenda com este ingrediente ativo' in pS)), [op[:4],disTD,dica[-160:],temT,ORDS(),pS[-160:]])   # revisão do CTL-5 (S3-1): só a ordem de pulverização
    # ---------- 16 · 1280×800: a grade inteira cabe (sem rolagem lateral) · LMR ausente é texto neutro, não vermelho ----------
    c.size(1280,800); c.goto(U_('AG-07.dc.html'),wait=.8); pronto()
    lay=J("(()=>{const r=document.querySelector('.g2rola'); const h=[...document.querySelectorAll('main [role=columnheader]')].pop().getBoundingClientRect(); return [r.scrollWidth,r.clientWidth,Math.round(h.right),innerWidth];})()") or [1,0,1,0]
    shot('lista_1280')
    canS=CU[SJ][2]
    def sem_lmr(x):
        for k in x['ids']:
            mono=LMR['monografias'].get(IG[k][2] or '')
            if mono and not any(nz(c_).replace('-',' ')==nz(canS) for c_ in mono[2]): return IG[k][0]
    XL=next(x for x in P if SJ in x['cul'] and len(x['ids'])==1 and sem_lmr(x))
    c.size(1440,900); J(f"location.hash='#reg-{XL['reg']}'"); time.sleep(.8); setv(f'{FX} select[aria-label="Cultura do uso"]',str(SJ))
    lm=J(f"[...document.querySelectorAll('{FX} [role=table][aria-label=\"LMR ANVISA\"] [role=cell]')].map(x=>[x.innerText.trim(),getComputedStyle(x).color])") or []
    chk(f'16 1280×800: grade sem rolagem lateral (última coluna até {lay[2]} px de {lay[3]}); {XL["nome"]} × Soja sem LMR → "Sem LMR de Soja nos dados abertos…", sem vermelho',
        lay[0]<=lay[1] and lay[2]<=lay[3] and len(lm)==2 and lm[1][0].startswith('Sem LMR de Soja nos dados abertos da ANVISA') and lm[1][1]!='rgb(180, 35, 24)', [lay,lm])
    junta('AG-07 todas/1280')
    # ---------- 17 · estado de erro com "Tentar de novo" e nenhum erro de execução ----------
    c.goto(U_('AG-07.dc.html?falha=1'),wait=1.5); t_err=J("(document.querySelector('main [role=alert]')||{}).innerText||''") or ''; shot('erro')
    J("window.__agFail=false"); clica('main','Tentar de novo'); rec=pronto(); junta('AG-07 erro')
    chk('17 índice indisponível → "Não foi possível carregar a base do AGROFIT" + "Tentar de novo" recarrega; sem erro de execução nas páginas',
        'Não foi possível carregar a base do AGROFIT' in t_err and rec and cnt()==f'{nf(NP,0)} de {nf(NP,0)} produtos' and not ERRS, [t_err,rec,ERRS[:4]])
finally:
    try:
        if c: c.close()
    finally: srv.terminate()
print(f'\nRESULTADO: {len(OK)}/{len(OK)+len(FAIL)} ok · {time.time()-t0:.0f} s', FAIL)
