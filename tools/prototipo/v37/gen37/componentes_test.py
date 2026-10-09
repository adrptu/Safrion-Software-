# -*- coding: utf-8 -*-
"""Teste CDP · componentes compartilhados (03/10/2026): QUALIDADE-ARTEFATO-20261003-FLUXO/RESPONSIVIDADE,
UX-FEEDBACK-INTERACAO-20261003 e MAPA-ICONES-20261003. 31 verificações em seis modos (cada um < 90 s):
  python3 componentes_test.py matriz     1-3   viewport do aparelho; matriz 360×800/800×360, 768×1024/1024×768, 1280×720/1440×900
                                               e zoom 200 % (720×450 a 2×) em SAF, CMP, O.S. e PA; menu estreito/largo
  python3 componentes_test.py rotacao    4-9   rotação com rascunho e com filtro/etapa/foco; painel da O.S.; App de campo; mapa; erros
  python3 componentes_test.py interacao  10-19 estados de interação por família (PA repouso→hover→saída, teclado, toque, linhas,
                                               indisponível, menos movimento, folha de etapas, menu sobreposto, tabela larga)
  python3 componentes_test.py icones     20-25 Satélite e Pragas e doenças no mapa (trilha e painel), estados, celular, capturas antes/depois
  python3 componentes_test.py ajustes    26-29 achados da verificação: tabela no celular (1ª coluna limitada, colunas e ações alcançáveis),
                                               menu com "aberto" guardado e Tab saindo do menu, áreas seguras emuladas, toque sem hover grudado
  python3 componentes_test.py ajustes2   30-31 foco inteiro e sem nada por cima no celular; proposta do IN-04 em 6 dimensões com o painel
Emulação no Chrome headless (largura e altura em px CSS, escala, toque, sem hover): não é aparelho físico nem Safari do iPhone.
Capturas em _probe/comp_*.png. Base para "antes": ANTES_DIR (padrão ../../base_v42/gen37/_render, senão ../gen37_antes/_render)."""
import sys, os, time, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from comp_lib import Chrome, servir, MEDE, resumo
MODO=sys.argv[1] if len(sys.argv)>1 else 'matriz'
PROBE=os.path.join(HERE,'_probe'); os.makedirs(PROBE,exist_ok=True)
OK=[]; FAIL=[]
def chk(nome,cond,info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,('' if cond else str(info)[:1200]),flush=True)
MAT=[('360x800',360,800,3,True),('800x360',800,360,3,True),('768x1024',768,1024,2,True),('1024x768',1024,768,2,True),
     ('1280x720',1280,720,1,False),('1440x900',1440,900,1,False),('zoom200',720,450,2,False)]
p,srv=servir(os.environ.get('RENDER_DIR') or os.path.join(HERE,'_render')); c=None; ERRL=[]   # RENDER_DIR: rodar contra outro build (ex.: o anterior)
def errs(): return [e for e in (c.js("window.__errs||[]") or []) if "reading 'g2toast'" not in e]
def abre(pg,w=1440,h=900,e=1,t=False,rec=None,espera=.6):
    ERRL.extend(errs()) if c else None
    c.aparelho(w,h,e,t)
    if rec is not None:
        c.goto(f'http://127.0.0.1:{p}/Main.dc.html',.2)
        c.js("localStorage.removeItem('safrion.menuRecolhido')" if rec=='' else f"localStorage.setItem('safrion.menuRecolhido','{rec}')")
    c.goto(f'http://127.0.0.1:{p}/{pg}.dc.html',espera)
def shot(nome): c.shot(os.path.join(PROBE,f'comp_{"anterior_" if os.environ.get("RENDER_DIR") else ""}{nome}.png'))
def centro(sel):
    return c.js(f"(()=>{{const e={sel}; if(!e) return null; e.scrollIntoView({{block:'center',inline:'nearest'}}); const r=e.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];}})()")
def estilo(sel,props):
    return c.js(f"(()=>{{const e={sel}; if(!e) return null; const cs=getComputedStyle(e); return {json.dumps(props)}.map(k=>cs.getPropertyValue(k));}})()")
def rect(sel): return c.js(f"(()=>{{const e={sel}; if(!e) return null; const r=e.getBoundingClientRect(); return [Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)];}})()")
N="(s=>(s||'').replace(/\\s+/g,' ').trim())"
try:
    c=Chrome()
    if MODO=='matriz':
        # 1 · meta viewport: no celular a página usa a largura do aparelho (antes desenhava em 980 px e encolhia tudo)
        abre('SAF',360,800,3,True,rec=''); a=c.js("document.querySelector('[data-root]').getBoundingClientRect().width")
        abre('MB-01',360,800,3,True); b=c.js("document.querySelector('[data-mroot]').getBoundingClientRect().width")
        abre('OS-0424-app',360,800,3,True); o=c.js("Math.round(document.documentElement.getBoundingClientRect().width)")
        chk('1 viewport do aparelho · casca e App de campo com a largura do celular (360 px), sem desenho em 980 px reduzido', a==360 and b==360, [a,b])
        print(f'     (informativo, pendência os_campo.py) OS-0424-app ainda desenha em {o} px no celular')
        # 2 · matriz: SAF, CMP, O.S. e PA nas 7 dimensões (1ª visita, sem escolha de menu guardada)
        prob={}; util={}
        for tag,w,h,e,t in MAT:
            for pg in ('SAF','CMP','OS','PA'):
                abre(pg,w,h,e,t,rec='' if (tag,pg)==(MAT[0][0],'SAF') else None); m=c.js(MEDE); r=resumo(m)
                if r: prob[f'{pg} {tag}']=r
                util[f'{pg} {tag}']=(m.get('util'),m.get('menu'),m.get('etapa','')[:24]); shot(f'{pg}_{tag}')
        chk('2 matriz 7 dimensões × SAF, CMP, O.S., PA · título, comando principal e etapa atual visíveis/alcançáveis, nada cortado fora de região rolável, sem rolagem lateral da página, fonte ≥ 10 px, sem escala global', not prob, prob)
        print('     (informativo) área útil, menu e etapa:', {k:v for k,v in util.items() if k.startswith(('SAF','OS'))})
        # 3 · menu: estreito (≤ 1023 px) começa recolhido na 1ª visita e abre por cima com fundo; largo fica ao lado
        larg={}
        for tag,w,h,e,t in (MAT[0],MAT[2],MAT[6],MAT[3],MAT[5]):
            abre('CMP',w,h,e,t,rec=''); larg[tag]=c.js("(()=>{const m=document.querySelector('.menu-lat'); return [Math.round(m.getBoundingClientRect().width),getComputedStyle(m).position];})()")
        abre('CMP',768,1024,2,True,rec=''); c.js("document.querySelector('.ml-tog').click()"); time.sleep(.35)
        ab=c.js("(()=>{const m=document.querySelector('.menu-lat'); const f=document.querySelector('.ml-fundo'); return [Math.round(m.getBoundingClientRect().width),getComputedStyle(m).position,getComputedStyle(f).display,localStorage.getItem('safrion.menuRecolhido')];})()"); shot('menu_768_aberto_sobreposto')
        xy=c.js("[700,600]"); c.toque(*xy); fe=c.js("[Math.round(document.querySelector('.menu-lat').getBoundingClientRect().width),localStorage.getItem('safrion.menuRecolhido')]")
        chk('3 menu · 1ª visita: recolhido (68 px) em 360, 768 e zoom 200 %, ao lado (232 px) em 1024 e 1440; no estreito abre por cima com fundo, o toque no fundo fecha e a escolha guardada não muda',
            larg['360x800'][0]==68 and larg['768x1024'][0]==68 and larg['zoom200'][0]==68 and larg['1024x768']==[232,'static'] and larg['1440x900']==[232,'static'] and ab[:3]==[232,'absolute','block'] and ab[3] is None and fe==[68,None], [larg,ab,fe])
        ERRL.extend(errs()); print('     erros JS (matriz):',ERRL[:3])
    elif MODO=='rotacao':
        # 4 · rotação com rascunho: IR-02 · painel "Programar período" com texto digitado; girar 360×800 → 800×360 → 360×800
        abre('IR-02',360,800,3,True,rec=''); c.js("window.__marca=1; [...document.querySelectorAll('header button,main button')].find(b=>b.innerText.trim()==='Programar irrigação').click()   // rótulo atual do comando da IR-02 (o teste procurava o da v41)"); time.sleep(.5)
        campo=c.js("(()=>{const i=[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] textarea')].find(x=>x.getClientRects().length&&!x.readOnly&&!x.disabled&&(x.type==='text'||x.tagName==='TEXTAREA')); if(!i) return null; i.focus(); return i.id;})()")
        esc=None
        if campo: c.call('Input.insertText',{'text':'rascunho girando 03/10'})
        else:   # o painel "Programar irrigação" da v43 não tem campo de texto livre: o rascunho é a escolha feita num seletor do painel
            esc=c.js("(()=>{const s=[...document.querySelectorAll('aside[role=dialog] select')].find(x=>x.getClientRects().length&&!x.disabled&&x.options.length>1); if(!s) return null; const o=[...s.options].find(x=>x.value&&x.value!==s.value); if(!o) return null; const P=HTMLSelectElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(s,o.value); s.dispatchEvent(new Event('change',{bubbles:true})); if(!s.id) s.id='rot-sel'; s.focus(); return [s.id,o.value];})()")
            campo=esc[0] if esc else None
        time.sleep(.3); m1=c.js(MEDE); shot('IR-02_360x800_rascunho')
        c.aparelho(800,360,3,True); time.sleep(.4); m2=c.js(MEDE); shot('IR-02_800x360_rascunho'); c.aparelho(360,800,3,True); time.sleep(.4)
        fim=c.js(f"[(document.getElementById({json.dumps(campo)})||{{value:null}}).value, window.__marca===1, !!document.querySelector('aside[role=dialog]'), document.activeElement&&document.activeElement.id]")
        chk('4 rotação com rascunho (IR-02 · Programar irrigação) · painel continua aberto com o texto/escolha feita, sem recarregar; Fechar e Salvar alcançáveis em pé e deitado; foco no campo',
            bool(campo) and fim[0] and ((fim[0]==esc[1]) if esc else ('rascunho girando 03/10' in fim[0])) and fim[1] and fim[2] and fim[3]==campo and m1.get('painelFechar') and m1.get('painelPrimOk') and m2.get('painelFechar') and m2.get('painelPrimOk') and not m2.get('painelFora'),
            [campo,fim,{k:m1.get(k) for k in ('painel','painelFechar','painelPrim','painelPrimOk')},{k:m2.get(k) for k in ('painel','painelFechar','painelPrim','painelPrimOk')}])
        # 5 · rotação com filtro e etapa: O.S. safra escolhida; CMP etapa 2 e foco na etapa atual (faixa completa → compacta)
        abre('OS',768,1024,2,True); c.js("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por safra\"]'); s.value='2026/27'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.4)
        c.aparelho(1024,768,2,True); time.sleep(.4); s1=c.js("document.querySelector('select[aria-label=\"Filtrar por safra\"]').value"); c.aparelho(768,1024,2,True); time.sleep(.3); s2=c.js("document.querySelector('select[aria-label=\"Filtrar por safra\"]').value")
        abre('CMP',1440,900); c.js(f"[...document.querySelectorAll('main button,main a')].find(b=>{N}(b.innerText)==='Abrir compra').click()"); time.sleep(.5)
        c.js("document.querySelector('[data-acoes] [data-acao=avancar]').focus()"); f1=c.js("[document.activeElement.innerText.replace(/\\s+/g,' ').trim(), (document.querySelector('.etp-itens [aria-current=step]')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim()]")
        c.aparelho(390,844,3,True); time.sleep(.6); f2=c.js("[document.activeElement.innerText.replace(/\\s+/g,' ').trim(), (document.querySelector('.etp-atual:not([style*=none])')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim()]"); shot('CMP_390_foco_apos_girar')
        c.aparelho(1440,900); time.sleep(.4); f3=c.js("[document.activeElement.innerText.replace(/\\s+/g,' ').trim(), (document.querySelector('.etp-itens [aria-current=step]')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim()]")
        chk('5 rotação/redimensionamento · safra escolhida na O.S. continua; CMP mantém a etapa 2 e o foco no avanço da área de ações ("Solicitar cotações ›") em 1440 → 390 → 1440, com "Etapa 2 de 6" na faixa compacta (UX-ACAO-UNICA)',
            s1=='2026/27' and s2=='2026/27' and f1[0].startswith('Solicitar cotações') and f1[1].startswith('2 ') and f2[0].startswith('Solicitar cotações') and f2[1].startswith('Etapa 2 de 6') and f3[0].startswith('Solicitar cotações') and f3[1].startswith('2 '), [s1,s2,f1,f2,f3])
        # 6 · O.S.: painel da ordem no celular em pé e deitado (largura, fechar e ação alcançáveis)
        res={}
        for tag,w,h,e,t in (MAT[0],MAT[1],MAT[6]):
            abre('OS',w,h,e,t); c.js("(()=>{const r=document.querySelector('[role=row].g2ed'); (r.querySelector('[role=cell] b')||r).click();})()"); time.sleep(.5)
            m=c.js(MEDE); res[tag]=(m.get('painel'),m.get('painelFora'),m.get('painelFechar'),m.get('painelPrim'),m.get('painelPrimOk')); shot(f'OS_{tag}_painel')
        chk('6 O.S. · painel da ordem dentro da tela em 360×800, 800×360 e zoom 200 %, com Fechar e ação principal alcançáveis', all(v[0] and not v[1] and v[2] and v[4] for v in res.values()), res)
        # 7 · App de campo (MB-01, MB-03): cabeçalho inteiro e comando grande visível sem rolar, em pé e deitado
        res={}
        for pg in ('MB-01','MB-03'):
            for tag,w,h,e,t in (MAT[0],MAT[1],MAT[2]):
                abre(pg,w,h,e,t); res[f'{pg} {tag}']=c.js("(()=>{const r=document.querySelector('[data-mroot]'); const a=r.querySelector(':scope>main+div a,:scope>main+div button'); const b=a.getBoundingClientRect(); const h=document.elementFromPoint(b.left+b.width/2,b.top+b.height/2); const t=r.querySelector('h1').getBoundingClientRect(); return [Math.round(r.getBoundingClientRect().width),b.bottom<=innerHeight+1&&!!h&&a.contains(h),t.top>=0&&t.right<=innerWidth+1];})()")
                shot(f'{pg}_{tag}')
        chk('7 App de campo · raiz com a largura do aparelho (até 720 px), título inteiro e comando principal visível sem rolar (360×800, 800×360, 768×1024)', all(v[1] and v[2] for v in res.values()) and res['MB-01 360x800'][0]==360, res)
        # 8 · mapa (IN-04): trilha e painel no celular. A disposição é de inicio.py (fora deste recorte): mede o estado atual e
        #     valida por injeção o CSS proposto como pendência (comp_in04_proposta.css)
        PROP=open(os.path.join(HERE,'comp_in04_proposta.css')).read()
        MAPA="""(()=>{const tb=document.querySelector('main [aria-label="Ferramentas do mapa"]'); const m=tb&&tb.parentElement; const a=document.querySelector('main aside[aria-label]');
          const fora=a?[...a.querySelectorAll('button,a')].filter(e=>e.getClientRects().length&&(e.getBoundingClientRect().right>innerWidth+1)).length:-1;
          return {mapaW:m?Math.round(m.getBoundingClientRect().width):0, mapaH:m?Math.round(m.getBoundingClientRect().height):0, painelW:a?Math.round(a.getBoundingClientRect().width):0, botoesFora:fora};})()"""
        def in04(inj):
            abre('IN-04',360,800,3,True); c.js("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); s.value='Santa Rita'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.5)
            if inj: c.js("(()=>{const t=document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"]'); t.classList.add('mapa-trilha'); t.parentElement.classList.add('mapa-corpo'); const st=document.createElement('style'); st.textContent="+json.dumps(PROP)+"; document.head.appendChild(st);})()")
            c.js("document.querySelector('polygon[role=button]').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); time.sleep(.5)
            if inj: c.js("(()=>{const ar=document.querySelector('main [aria-label=\"Ferramentas do mapa\"]').parentElement; ar.classList.add('mapa-area'); ar.parentElement.closest('div').classList.add('mapa-linha');})()"); time.sleep(.3)
            r=c.js(MAPA); shot('IN-04_360x800_'+('proposta' if inj else 'atual')); return r
        at=in04(False); pr=in04(True)
        print('     (informativo, pendência inicio.py) IN-04 360×800 hoje:',at)
        chk('8 mapa IN-04 · proposta para inicio.py validada por injeção em 360×800: mapa ≥ 250 px de largura e ≥ 280 px de altura, painel do talhão na largura da tela com todos os botões dentro',
            pr['mapaW']>=250 and pr['mapaH']>=280 and 0<pr['painelW']<=300 and pr['botoesFora']==0, [at,pr])
        ERRL.extend(errs()); chk('9 sem erro de JS nas telas visitadas (matriz e rotação)', not ERRL, ERRL[:5])
    elif MODO=='interacao':
        CARD="document.querySelectorAll('main .g2card')[0]"
        def mouse_em(sel):
            xy=centro(sel); c.mouse(*xy); time.sleep(.15); return xy
        # 10 · PA: repouso → hover → saída, sem selecionar e sem salto de layout; pista "Abrir plano →" permanente
        abre('PA',1440,900)
        r0=rect(CARD); e0=estilo(CARD,['background-color','border-top-color','cursor']); cta=c.js(f"(()=>{{const e={CARD}.querySelector('.g2card-cta'); const r=e.getBoundingClientRect(); return [e.innerText.replace(/\\s+/g,' ').trim(), r.width>0&&getComputedStyle(e).visibility!=='hidden'];}})()"); shot('PA_1440_repouso')
        xy=mouse_em(CARD); e1=estilo(CARD,['background-color','border-top-color']); r1=rect(CARD); shot('PA_1440_hover')
        c.mouse(5,450); time.sleep(.15); e2=estilo(CARD,['background-color','border-top-color']); cur=c.js(f"{CARD}.getAttribute('aria-current')")
        chk('10 PA · repouso branco com "Abrir plano →" visível; hover muda fundo e borda; ao sair volta; nada selecionado; mesmo tamanho e posição',
            cta[0]=='Abrir plano →' and cta[1] and e0[0]=='rgb(255, 255, 255)' and e0[2]=='pointer' and e1[0]=='rgb(242, 248, 244)' and e1[1]=='rgb(157, 191, 170)' and e2[:2]==e0[:2] and cur=='false' and r0==r1, [cta,e0,e1,e2,cur,r0,r1])
        # 11 · teclado: filtro Soja → Tab até o cartão (foco nítido, não cortado) → pressionado → Enter abre o plano (uma vez) → volta à etapa 1:
        #      filtro e posição conservados, cartão aberto por último marcado (persistente, diferente de hover/foco)
        c.js(f"[...document.querySelectorAll('[aria-label=\"Filtrar planos por cultura\"] button')].find(b=>{N}(b.innerText).startsWith('Soja')).click()"); time.sleep(.3)
        c.js("document.querySelector('[aria-label=\"Filtrar planos por cultura\"] button[aria-pressed=true]').focus()")
        k=0
        while k<30 and not c.js("document.activeElement&&document.activeElement.classList.contains('g2card')"): c.tab(); k+=1
        nome=c.js("document.activeElement.getAttribute('aria-label')"); ef=c.js("(()=>{const e=document.activeElement; const cs=getComputedStyle(e); const r=e.getBoundingClientRect(); let ok=true; for(let p=e.parentElement;p;p=p.parentElement){ const s=getComputedStyle(p); if(s.overflow!=='visible'||s.overflowX!=='visible'){ const q=p.getBoundingClientRect(); if(r.left-4<q.left||r.right+4>q.right||r.top-4<q.top) { ok=false; break; } } } return [e.matches(':focus-visible'),cs.outlineStyle,cs.outlineWidth,cs.outlineColor,ok];})()"); shot('PA_1440_foco')
        xy=centro("document.activeElement"); c.mouse(*xy,'mousePressed','left'); ea=estilo("document.activeElement",['background-color','filter']); c.mouse(5,450,'mouseMoved','left'); c.mouse(5,450,'mouseReleased','left'); time.sleep(.2)
        c.js("window.__toasts=[]; new MutationObserver(()=>{const t=document.querySelector('[role=status]'); if(t&&t.innerText.trim()) window.__toasts.push(t.innerText.trim());}).observe(document.body,{subtree:true,childList:true,characterData:true})")
        c.js(f"[...document.querySelectorAll('main .g2card')].find(b=>b.getAttribute('aria-label')==={json.dumps(nome)}).focus()")
        c.tecla('Enter','Enter',13,text='\r'); time.sleep(.5)
        st2=c.js("location.hash"); toasts=c.js("[...new Set(window.__toasts)]")   # NAV-1: o plano abre no detalhe (#plano=), sem etapas
        c.js("document.querySelector('[data-acoes] [data-acao=voltar]').click()"); time.sleep(.5)
        volta=c.js(f"(()=>{{const f=document.querySelector('[aria-label=\"Filtrar planos por cultura\"] button[aria-pressed=true]'); const cs=[...document.querySelectorAll('main .g2card')]; const a=cs.find(b=>b.getAttribute('aria-current')==='true'); return [f?{N}(f.innerText):'', a?a.getAttribute('aria-label'):'', a?getComputedStyle(a).borderTopColor:'', a?getComputedStyle(a,'::after').content:'', cs.length];}})()"); shot('PA_1440_volta_selecionado')
        chk('11 PA teclado · Tab chega ao cartão com contorno de 2 px não cortado; pressionado escurece; Enter abre o plano uma vez (detalhe #plano=); "‹ Biblioteca de planos" (área de ações) volta com filtro Soja, cartão aberto marcado (borda verde + "Último aberto")',
            k<30 and ef[0] and ef[1]=='solid' and ef[2]=='2px' and ef[4] and ea[0]=='rgb(228, 243, 233)' and st2.startswith('#plano=') and len([t for t in toasts if t.startswith('Plano aberto')])==1
            and volta[0].startswith('Soja') and volta[1]==nome and volta[2]=='rgb(30, 122, 76)' and 'Último aberto' in volta[3] and volta[4]==2, [k,ef,ea,st2,toasts,volta])
        # 12 · toque (sem hover, 390 px): passar o "dedo" não pinta hover; rolar até o último cartão, um toque abre o plano;
        #      ‹ volta à biblioteca na mesma posição de rolagem, com o foco no cartão aberto
        abre('PA',390,844,3,True); hv=c.js("matchMedia('(hover: hover)').matches")
        ULT="[...document.querySelectorAll('main .g2card')].pop()"
        xy=centro(ULT); c.mouse(*xy); time.sleep(.15); eh=estilo(ULT,['background-color'])
        rol="[...document.querySelectorAll('main[data-scroll],.ml-tog+div')].map(e=>Math.round(e.scrollTop))"
        antes=c.js(rol); nome=c.js(f"{ULT}.getAttribute('aria-label')")
        c.toque(*xy); st=c.js("location.hash"); shot('PA_390_toque_aberto')   # NAV-1: detalhe #plano=, sem etapas
        c.js("document.querySelector('[data-acoes] [data-acao=voltar]').click()"); time.sleep(.5)
        depois=c.js(rol); foco=c.js("document.activeElement&&document.activeElement.getAttribute('aria-label')"); shot('PA_390_volta_posicao')
        chk('12 toque sem hover (390 px) · sem pintura de hover; um toque no último cartão abre o plano; "‹ Biblioteca de planos" volta à mesma posição de rolagem com o foco no cartão aberto',
            not hv and eh[0]=='rgb(255, 255, 255)' and st.startswith('#plano=') and max(antes)>200 and all(abs(a-b)<=2 for a,b in zip(antes,depois)) and foco==nome, [hv,eh,st,antes,depois,foco,nome])
        # 13 · linha da grade com controle interno (CD-06): Enter/Espaço no expandir só expande/recolhe; Enter na linha abre o detalhe uma vez
        abre('CD-06',1440,900)
        CAR="document.querySelector('[role=row].g2ed .g2car')"
        a0=c.js(f"{CAR}.getAttribute('aria-expanded')"); c.js(f"{CAR}.focus()"); c.tecla('Enter','Enter',13,text='\r'); time.sleep(.35)
        a1=c.js(f"[{CAR}.getAttribute('aria-expanded'), !!document.querySelector('aside[role=dialog]')]"); c.js(f"{CAR}.focus()"); c.tecla(' ','Space',32,text=' '); time.sleep(.35)
        a2=c.js(f"[{CAR}.getAttribute('aria-expanded'), !!document.querySelector('aside[role=dialog]')]")
        c.js("document.querySelectorAll('[role=row].g2ed')[1].focus()"); c.tecla('Enter','Enter',13,text='\r'); time.sleep(.4); d=c.js("document.querySelectorAll('aside[role=dialog]').length")
        chk('13 linha com controle interno (CD-06) · Enter e Espaço no expandir alternam aria-expanded sem abrir o formulário; Enter na linha abre 1 formulário', a0 in ('true','false') and a1[0]!=a0 and not a1[1] and a2[0]==a0 and not a2[1] and d==1, [a0,a1,a2,d])
        # 14 · uma ocorrência por família (hover/foco/pressionado) e conteúdo inerte sem cara de ação
        fam={}
        abre('PA',1440,900)
        NOVO=f"[...document.querySelectorAll('header button')].find(b=>{N}(b.innerText)==='Criar plano')"   # NAV-1/BOT-03: "Criar plano" no cabeçalho
        mouse_em(NOVO); fam['botão primário hover']=estilo(NOVO,['filter'])[0]
        MEN="[...document.querySelectorAll('.menu-lat a')].find(a=>a.innerText.trim()==='Planejar safra')"
        mouse_em(MEN); fam['menu hover']=estilo(MEN,['box-shadow'])[0]
        CHP=f"[...document.querySelectorAll('[aria-label=\"Filtrar planos por cultura\"] button')].find(b=>{N}(b.innerText).startsWith('Milho'))"
        mouse_em(CHP); fam['chip hover']=estilo(CHP,['box-shadow','filter'])
        INE="[...document.querySelectorAll('main div')].find(d=>/^soja\s*·/i.test(d.textContent.trim()))"; mouse_em(INE); fam['texto inerte']=estilo(INE,['cursor','filter','box-shadow'])
        abre('SAF',1440,900); BUS="document.querySelector('main input[type=search]')"
        STP="document.querySelectorAll('.etp-itens>*')[1]"   # NAV-1: a PA não tem mais faixa; a etapa inerte é medida no Planejar safra
        mouse_em(STP); fam['etapa inerte']=estilo(STP,['filter','cursor','box-shadow'])   # UX-ACAO-UNICA: a faixa só informa
        mouse_em(BUS); fam['busca hover']=estilo(f"{BUS}.closest('label')",['box-shadow'])[0]
        c.js(f"{BUS}.focus()"); fam['busca foco']=estilo(f"{BUS}.closest('label')",['outline-style','outline-color'])
        abre('IN-04',1440,900); c.js("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); s.value='Santa Rita'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.5)
        c.js("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').focus()"); k=0
        while k<60 and not c.js("document.activeElement&&document.activeElement.matches('polygon[role=button]')"): c.tab(); k+=1
        fam['talhão foco']=estilo("document.activeElement",['stroke-dasharray','stroke']); shot('IN-04_1440_talhao_foco')
        TB="document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')[1]"
        mouse_em(TB); fam['trilha hover']=estilo(TB,['box-shadow'])[0]
        print('     (informativo) famílias:',fam)
        fam_ok=(fam['texto inerte'][0]!='pointer' and fam['texto inerte'][1]=='none' and fam['texto inerte'][2]=='none'
                and 'brightness(0.95)' in fam['botão primário hover'] and '255, 255, 255' in fam['menu hover'] and 'inset' in fam['chip hover'][0] and fam['etapa inerte'][0]=='none' and fam['etapa inerte'][1]!='pointer' and fam['etapa inerte'][2]=='none'
                and 'rgb(157, 191, 170)' in fam['busca hover'] and fam['busca foco'][0]=='solid' and fam['talhão foco'][0].replace(' ','').replace('px','').startswith('7,4') and 'inset' in fam['trilha hover'])
        chk('14 famílias · botão, menu, chip, busca (hover e foco), talhão do mapa (foco tracejado) e trilha do mapa respondem; título de seção e etapa da faixa (inertes) sem cursor de ação nem hover', fam_ok, fam)
        # 15 · indisponível: OK do filtro sem valor marcado fica diferente, cursor de proibido e motivo em texto (role=alert)
        abre('OS',1440,900); c.js("document.querySelector('.g2fb').click()"); time.sleep(.3)
        c.js("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Limpar'||b.innerText.trim()==='Nenhum'||/desmarcar/i.test(b.innerText))?.click()"); time.sleep(.25)
        dis=c.js("(()=>{const ok=[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='OK'); const al=[...document.querySelectorAll('[role=dialog] [role=alert]')].map(a=>a.innerText.trim()); return ok?[ok.disabled,getComputedStyle(ok).opacity,getComputedStyle(ok).cursor,al]:null;})()"); shot('OS_1440_ok_indisponivel')
        chk('15 indisponível · OK do filtro sem valor marcado: desabilitado, opacidade menor, cursor de proibido e motivo "Marque pelo menos um valor." em texto', bool(dis) and dis[0] and float(dis[1])<0.7 and dis[2]=='not-allowed' and any('Marque pelo menos um valor' in a for a in dis[3]), dis)
        # 16 · menos movimento: com prefers-reduced-motion, as transições do menu e da seta da faixa ficam instantâneas
        c.call('Emulation.setEmulatedMedia',{'features':[{'name':'prefers-reduced-motion','value':'reduce'}]}); c.goto(f'http://127.0.0.1:{p}/CMP.dc.html',.4)
        rm=c.js("[getComputedStyle(document.querySelector('.menu-lat')).transitionDuration,getComputedStyle(document.querySelector('.ml-tog')).transitionDuration]")
        c.call('Emulation.setEmulatedMedia',{'features':[]}); c.goto(f'http://127.0.0.1:{p}/CMP.dc.html',.4); rn=c.js("getComputedStyle(document.querySelector('.menu-lat')).transitionDuration")
        chk('16 menos movimento · com redução pedida a transição do menu cai a ~0 s; sem pedido continua 0,18 s', all(float(x.split(',')[0].rstrip('s'))<0.001 for x in rm) and rn.startswith('0.18'), [rm,rn])
        # 17 · folha de etapas pelo teclado (390 px): Enter abre, Esc fecha com o foco no rótulo; escolher etapa pelo teclado devolve o foco ao rótulo
        abre('CMP',390,844,3,False); c.js(f"[...document.querySelectorAll('main button,main a')].find(b=>{N}(b.innerText)==='Abrir compra').click()"); time.sleep(.4)
        c.js("[...document.querySelectorAll('.etp-chk')].find(x=>x.getClientRects().length).focus()"); c.tecla('Enter','Enter',13,text='\r'); time.sleep(.25)
        f1=c.js("[...document.querySelectorAll('.etp-chk')].find(x=>x.getClientRects().length).checked"); c.tecla('Escape','Escape',27); time.sleep(.25)
        f2=c.js("(()=>{const k=[...document.querySelectorAll('.etp-chk')].find(x=>x.getClientRects().length); return [k.checked, document.activeElement===k];})()")
        c.tecla('Enter','Enter',13,text='\r'); time.sleep(.25); shot('CMP_390_folha_teclado'); c.tab()
        dentro=c.js("!!(document.activeElement&&document.activeElement.closest('.etp-itens'))"); c.tecla('Escape','Escape',27); time.sleep(.25)
        f3=c.js("(()=>{const k=[...document.querySelectorAll('.etp-chk')].find(x=>x.getClientRects().length); return [k.checked, (document.querySelector('.etp-atual:not([style*=none])')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim().slice(0,30), document.querySelectorAll('.etp-itens button,.etp-itens a,.etp-itens [tabindex]').length];})()")
        chk('17 folha de etapas pelo teclado · Enter abre, Esc fecha e o foco fica no rótulo; a lista só informa: o Tab não entra nela, nenhum item é botão/link e a etapa continua a 2 (UX-ACAO-UNICA)', f1 and f2==[False,True] and not dentro and f3[0]==False and f3[1].startswith('Etapa 2 de 6') and f3[2]==0, [f1,f2,dentro,f3])
        # 18 · menu sobreposto (390 px): Esc fecha e devolve o foco ao botão do menu
        abre('CMP',390,844,3,False,rec=''); c.js("document.querySelector('.ml-tog').click()"); time.sleep(.3); w1=c.js("Math.round(document.querySelector('.menu-lat').getBoundingClientRect().width)")
        c.js("document.querySelector('.menu-lat a').focus()"); c.tecla('Escape','Escape',27); time.sleep(.35)
        w2=c.js("[Math.round(document.querySelector('.menu-lat').getBoundingClientRect().width), document.activeElement===document.querySelector('.ml-tog')]")
        chk('18 menu sobreposto · Esc fecha (232 → 68 px) e o foco volta ao botão do menu', w1==232 and w2==[68,True], [w1,w2])
        # 19 · tabela mais larga que a tela (SAF 390 px): borda direita esmaecida enquanto há colunas à direita; some ao rolar até o fim
        abre('SAF',390,844,3,False); time.sleep(.4); m1=c.js("(()=>{const r=document.querySelector('main .g2rola'); return [r.scrollWidth>r.clientWidth, r.hasAttribute('data-mais'), getComputedStyle(r).webkitMaskImage||getComputedStyle(r).maskImage];})()"); shot('SAF_390_tabela_mais')
        c.js("(()=>{const r=document.querySelector('main .g2rola'); r.scrollLeft=r.scrollWidth;})()"); time.sleep(.4); m2=c.js("document.querySelector('main .g2rola').hasAttribute('data-mais')")
        chk('19 tabela larga (SAF 390 px) · rola dentro da caixa com a borda direita esmaecida; no fim da rolagem o esmaecimento some', m1[0] and m1[1] and 'gradient' in str(m1[2]) and not m2, [m1,m2])
        ERRL.extend(errs()); print('     erros JS (interação):',ERRL[:3])
    elif MODO=='ajustes':
        # 26 · tabela no celular: a 1ª coluna presa fica limitada (≤ 45 % da caixa, nunca abaixo da maior palavra) e nenhuma outra
        #      coluna passa da área visível: todas as colunas aparecem ao rolar; todo controle da 1ª linha e do cabeçalho fica inteiro
        #      à vista ao receber o foco (fora da coluna presa); nada vaza da coluna presa. Em 1440 px a SAF fica como a base.
        TAB=r"""(async()=>{const r=[...document.querySelectorAll('main .g2rola')].find(x=>x.getClientRects().length); r.scrollIntoView({block:'start'}); const n=s=>(s||'').replace(/\s+/g,' ').trim();
          const hr=r.querySelector('[role=table]>[role=row]'); const st=hr.querySelector('.g2c0')||[...hr.querySelectorAll('[role=columnheader]')].find(x=>getComputedStyle(x).position==='sticky'); const row=r.querySelector('[role=row].g2r'); const y=()=>row.getBoundingClientRect().top+row.getBoundingClientRect().height/2;
          const cols=new Set(); for(let sl=0;sl<=r.scrollWidth;sl+=40){ r.scrollLeft=sl; const q=r.getBoundingClientRect(); for(let x=q.left+2;x<q.right-1;x+=4){ const h=document.elementFromPoint(x,y()); const c=h&&h.closest('[role=cell]'); if(c&&c.parentElement===row||c&&c.closest('[role=row]')===row) cols.add([...row.querySelectorAll('[role=cell]')].indexOf(c)); } }
          const ruins=[]; for(const b of [...row.querySelectorAll('a,button,input')].concat([...hr.querySelectorAll('button')])){ r.scrollLeft=0; b.focus(); await new Promise(z=>setTimeout(z,40));
            const br=b.getBoundingClientRect(), sr=st.getBoundingClientRect(), q=r.getBoundingClientRect(); const h=document.elementFromPoint(Math.min(Math.max(br.left+br.width/2,1),innerWidth-1),br.top+br.height/2);
            const cs=b.closest('[role=cell],[role=columnheader]'); if(!(h&&(h===b||b.contains(h))&&((cs&&getComputedStyle(cs).position==='sticky')||br.left>=sr.right-1)&&br.right<=q.right+1)) ruins.push(n(b.innerText||b.getAttribute('aria-label')).slice(0,24)); }
          const vaza=[...r.querySelectorAll('[role=cell],[role=columnheader]')].filter(x=>getComputedStyle(x).position==='sticky').flatMap(c=>{const cr=c.getBoundingClientRect(); return [...c.querySelectorAll('*')].filter(e=>e.getClientRects().length&&e.getBoundingClientRect().right>cr.right+1).map(e=>n(e.innerText).slice(0,20));});
          return {caixa:r.clientWidth, c0:Math.round(st.getBoundingClientRect().width), lim:r.hasAttribute('data-c0'), total:row.querySelectorAll('[role=cell]').length, vistas:[...cols].sort((a,b)=>a-b), ruins, vaza:vaza.slice(0,3)};})()"""
        res={}
        for pg in ('SAF','CMP','CD-06','SU-01','MA-01'):
            abre(pg,360,800,3,True,rec=''); res[pg]=c.js(TAB); shot(f'{pg}_360x800_tabela')
        abre('SAF',1440,900,rec=''); d1440=c.js("(()=>{const r=document.querySelector('main .g2rola'); return [r.hasAttribute('data-c0'), getComputedStyle(r.querySelector('[role=table]')).gridTemplateColumns.split(' ').length];})()")
        chk('26 tabela no celular (SAF, CMP, CD-06, SU-01, MA-01 em 360×800) · 1ª coluna limitada, todas as colunas aparecem ao rolar, todo controle da 1ª linha e do cabeçalho fica inteiro à vista com o foco, nada vaza da coluna presa; 1440 px sem limite',
            all(v['lim'] and v['c0']<=v['caixa']*0.62 and v['vistas']==list(range(v['total'])) and not v['ruins'] and not v['vaza'] for v in res.values()) and d1440[0] is False, [res,d1440])
        # 27 · menu com a escolha "aberto" guardada ('0', gravada no computador): no estreito toda tela começa recolhida e com o título
        #      livre; em 1440 fica aberto ao lado. No estreito, aberto pelo botão, Tab depois do último item fecha o menu e o foco segue
        g={}
        for tag,w,h,e,t in (MAT[0],MAT[2],MAT[6],MAT[5]):
            for pg in ('CMP','OS'):
                abre(pg,w,h,e,t,rec='0'); g[f'{pg} {tag}']=c.js("(()=>{const m=document.querySelector('.menu-lat'); const h1=document.querySelector('h1').getBoundingClientRect(); const hit=document.elementFromPoint(h1.left+5,h1.top+h1.height/2); return [Math.round(m.getBoundingClientRect().width), getComputedStyle(m).position, getComputedStyle(document.querySelector('.ml-fundo')).display, !!hit&&document.querySelector('h1').contains(hit)];})()")
        abre('CMP',768,1024,2,True,rec='0'); c.js("document.querySelector('.ml-tog').click()"); time.sleep(.35); ab=c.js("Math.round(document.querySelector('.menu-lat').getBoundingClientRect().width)")
        c.js("(()=>{const its=[...document.querySelectorAll('.menu-lat a,.menu-lat button')].filter(x=>x.getClientRects().length); its[its.length-1].focus();})()"); c.tab(); c.tab(); time.sleep(.35)
        tb=c.js("(()=>{const e=document.activeElement; return [Math.round(document.querySelector('.menu-lat').getBoundingClientRect().width), getComputedStyle(document.querySelector('.ml-fundo')).display, !!e.closest('.menu-lat'), (e.innerText||e.getAttribute('aria-label')||'').trim().slice(0,20), localStorage.getItem('safrion.menuRecolhido')];})()"); shot('menu_tab_fecha_768')
        chk('27 menu · com "aberto" guardado, CMP e O.S. começam recolhidos (68 px, sem fundo, título livre) em 360, 768 e zoom 200 %, e abertos ao lado em 1440; no estreito, Tab depois do último item fecha o menu e o foco segue no conteúdo; a escolha guardada não muda',
            all(v==[68,'static','none',True] for k,v in g.items() if '1440' not in k) and all(v[:2]==[232,'static'] for k,v in g.items() if '1440' in k) and ab==232 and tb[0]==68 and tb[1]=='none' and not tb[2] and tb[4]=='0', [g,ab,tb])
        # 28 · áreas seguras (Emulation.setSafeAreaInsetsOverride): deitado com entalhe nas laterais e em pé com entalhe no alto, o botão do
        #      menu e o menu sobreposto ficam dentro da área segura e o botão não cobre itens do menu
        SAFE="""(()=>{const R=e=>{const q=e.getBoundingClientRect(); return [Math.round(q.left),Math.round(q.top),Math.round(q.right),Math.round(q.bottom)];}; const tg=document.querySelector('.ml-tog'); const t=tg.getBoundingClientRect();
          const sob=[...document.querySelectorAll('.menu-lat a,.menu-lat button')].filter(x=>x.getClientRects().length).filter(x=>{const q=x.getBoundingClientRect(); return Math.min(q.right,t.right)-Math.max(q.left,t.left)>2&&Math.min(q.bottom,t.bottom)-Math.max(q.top,t.top)>2;}).length;
          return {menu:R(document.querySelector('.menu-lat')), tog:R(tg), sob};})()"""
        sa={}
        for (w,h,ins) in [(800,360,{'left':47,'right':47,'bottom':21,'top':0}),(360,800,{'top':47,'bottom':34,'left':0,'right':0})]:
            c.aparelho(w,h,3,True)
            try: c.call('Emulation.setSafeAreaInsetsOverride',{'insets':ins}); ok=True
            except Exception as ex: ok=False
            abre('SAF',w,h,3,True,rec=''); f=c.js(SAFE); c.js("document.querySelector('.ml-tog').click()"); time.sleep(.35); a=c.js(SAFE); shot(f'SAF_{w}x{h}_area_segura_menu')
            sa[f'{w}x{h}']=(ok,ins,f,a)
        try: c.call('Emulation.setSafeAreaInsetsOverride',{'insets':{}})
        except Exception: pass
        dent=lambda r,ins,w,h: r[0]>=ins['left']-1 and r[1]>=ins['top']-1 and r[2]<=w-ins['right']+1 and r[3]<=h-ins['bottom']+1
        chk('28 áreas seguras emuladas (800×360 com 47 px nas laterais; 360×800 com 47 px no alto) · botão do menu e menu aberto dentro da área segura; o botão não cobre itens do menu',
            all(v[0] and dent(v[2]['tog'],v[1],*map(int,k.split('x'))) and dent(v[3]['tog'],v[1],*map(int,k.split('x'))) and dent(v[3]['menu'],v[1],*map(int,k.split('x'))) and v[2]['sob']==0 and v[3]['sob']==0 for k,v in sa.items()), sa)
        # 29 · toque sem hover "grudado": expandir da grade (CD-06) e filtro de coluna (O.S.) voltam ao fundo transparente depois do toque
        tq={}
        for pg,sel in (('CD-06',"document.querySelectorAll('[role=row].g2ed .g2car')[1]"),('OS',"document.querySelector('.g2fb')")):
            abre(pg,360,800,3,True,rec=''); xy=centro(sel); c.toque(*xy); time.sleep(.3); tq[pg]=estilo(sel,['background-color'])[0]
            if pg=='OS': c.tecla('Escape','Escape',27)
        chk('29 toque (360×800, sem hover) · expandir da grade e filtro de coluna sem fundo de hover depois do toque', all(v in ('rgba(0, 0, 0, 0)','transparent') for v in tq.values()), tq)
        ERRL.extend(errs()); print('     erros JS (ajustes):',ERRL[:3])
    elif MODO=='ajustes2':
        # 30 · foco visível e inteiro no celular (360×800): caminhada de Tab em PA, O.S. e SAF; o contorno não é cortado pela área de
        #      rolagem nem fica por baixo da coluna/cabeçalho presos (o rótulo da faixa de etapas mostra o anel da caixa invisível)
        F=r"""(()=>{const e=document.activeElement; if(!e||e===document.body) return null; const n=s=>(s||'').replace(/\s+/g,' ').trim(); let host=e; if(e.classList.contains('etp-chk')) host=e.nextElementSibling; else if(e.type==='search'&&e.closest('label')) host=e.closest('label');
         const hs=getComputedStyle(host); const ring=hs.outlineStyle!=='none'&&parseFloat(hs.outlineWidth)>=1||(/polygon|circle/i.test(e.tagName)&&getComputedStyle(e).strokeDasharray!=='none'); const off=Math.max((parseFloat(hs.outlineOffset)||0)+(parseFloat(hs.outlineWidth)||0),0); const r=host.getBoundingClientRect();
         const R={l:r.left-off,t:r.top-off,r:r.right+off,b:r.bottom+off}; let corte=null; for(let p=host.parentElement;p;p=p.parentElement){ const s=getComputedStyle(p); if(s.position==='fixed') break; if(s.overflowX!=='visible'||s.overflowY!=='visible'){ const q=p.getBoundingClientRect(); if((s.overflowX!=='visible'&&(R.l<q.left-1||R.r>q.right+1))||(s.overflowY!=='visible'&&(R.t<q.top-1||R.b>q.bottom+1))){ corte=p.tagName+'.'+String(p.className).split(' ')[0]; break; } } }
         const x=Math.min(Math.max(r.left+r.width/2,1),innerWidth-1), y=Math.min(Math.max(r.top+r.height/2,1),innerHeight-1); const h=document.elementFromPoint(x,y); const cob=(h&&!(h===host||host.contains(h)||h.contains(host)&&h.tagName==='LABEL'))?n(h.innerText).slice(0,20):null;
         return {d:(e.tagName+':'+n(e.getAttribute('aria-label')||e.innerText)).slice(0,40), ring, corte, cob};})()"""
        fo={}
        for pg in ('PA','OS','SAF'):
            abre(pg,360,800,3,True,rec=''); c.js("document.activeElement&&document.activeElement.blur()"); ruins=[]; k=0
            for i in range(24):
                c.tab(); time.sleep(.12); f=c.js(F)
                if not f: continue
                k+=1
                if not f['ring'] or f['corte'] or f['cob']: ruins.append(f)
            fo[pg]=(k,ruins[:4])
        chk('30 foco no celular (360×800, 24 paradas de Tab em PA, O.S. e SAF) · contorno visível, inteiro (sem corte da área de rolagem) e sem nada por cima', all(v[0]>=20 and not v[1] for v in fo.values()), fo)
        # 31 · IN-04 (proposta para inicio.py, injetada): com o painel do talhão aberto, em 360×800, 800×360, 768×1024, 1024×768,
        #      1280×720 com o menu aberto e zoom 200 %: mapa útil (≥ 440 px ao lado do painel, senão o painel desce), nenhum controle do
        #      mapa sobre outro, painel na tela, página sem rolagem lateral; em 1440 sem painel a geometria do mapa é a da base
        PROP=open(os.environ.get('IN04_CSS') or os.path.join(HERE,'comp_in04_proposta.css')).read()   # IN04_CSS: validar outra versão da proposta
        INJ="(()=>{const t=document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"]'); t.classList.add('mapa-trilha'); t.parentElement.classList.add('mapa-corpo'); const ar=document.querySelector('main [aria-label=\"Ferramentas do mapa\"]').parentElement; ar.classList.add('mapa-area'); ar.parentElement.closest('div').classList.add('mapa-linha'); if(!document.getElementById('prop-in04')){ const st=document.createElement('style'); st.id='prop-in04'; st.textContent="+json.dumps(PROP)+"; document.head.appendChild(st);} })()"
        MP=r"""(()=>{const tb=document.querySelector('main [aria-label="Ferramentas do mapa"]'); const m=tb.parentElement; const a=document.querySelector('main aside[aria-label]'); const R=e=>e?(q=>[Math.round(q.left),Math.round(q.top),Math.round(q.width),Math.round(q.height)])(e.getBoundingClientRect()):null;
         const ctl=[...m.querySelectorAll(':scope>[role=toolbar] button,:scope>[role=group] button,:scope span[style*="top: 10px"],:scope>div[style*="bottom: 12px"]')].filter(e=>e.getClientRects().length&&e.getBoundingClientRect().width>2); const sob=[];
         for(let i=0;i<ctl.length;i++) for(let j=i+1;j<ctl.length;j++){ const A=ctl[i],B=ctl[j]; if(A.contains(B)||B.contains(A)) continue; const p=A.getBoundingClientRect(),q=B.getBoundingClientRect(); if(Math.min(p.right,q.right)-Math.max(p.left,q.left)>1&&Math.min(p.bottom,q.bottom)-Math.max(p.top,q.top)>1) sob.push((A.getAttribute('aria-label')||A.innerText).trim().slice(0,16)+' × '+(B.getAttribute('aria-label')||B.innerText).trim().slice(0,16)); }
         const fora=a?[...a.querySelectorAll('button,a')].filter(e=>e.getClientRects().length&&(e.getBoundingClientRect().right>innerWidth+1)).length:-1;
         return {mapa:R(m),painel:R(a),fora,sob,lado:document.documentElement.scrollWidth>innerWidth+1};})()"""
        mp={}
        for tag,w,h,e,t in (MAT[0],MAT[1],MAT[2],MAT[3],('1280x720 menu aberto',1280,720,1,False),MAT[6]):
            abre('IN-04',w,h,e,t,rec='')
            if 'menu aberto' in tag: c.js("document.querySelector('.menu-lat.rec')&&document.querySelector('.ml-tog').click()"); time.sleep(.3)
            c.js("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); s.value='Santa Rita'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.5)
            c.js(INJ); c.js("document.querySelector('polygon[role=button]').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); time.sleep(.5); c.js(INJ); time.sleep(.3)
            mp[tag]=c.js(MP); shot(f"IN-04_{tag.split(' ')[0]}_painel_proposta")
        abre('IN-04',1440,900,rec=''); base=c.js(MP)['mapa']; c.js(INJ); time.sleep(.3); prop=c.js(MP)['mapa']
        def ok(v):
            M,P=v['mapa'],v['painel']; lado=P and P[1]==M[1]
            return P and v['fora']==0 and not v['sob'] and not v['lado'] and M[3]>=280 and ((lado and M[2]>=440) or (not lado and M[2]>=250 and P[1]>=M[1]+M[3]-1))
        print('     (informativo) IN-04 proposta:',{k:(v['mapa'],v['painel']) for k,v in mp.items()})
        chk('31 IN-04 · proposta para inicio.py validada por injeção com o painel do talhão em 360×800, 800×360, 768×1024, 1024×768, 1280×720 (menu aberto) e zoom 200 %: mapa ≥ 440 px ao lado do painel ou painel abaixo do mapa (≥ 250 × 280 px), nenhum controle do mapa sobre outro, painel na tela; 1440 px sem painel igual',
            all(ok(v) for v in mp.values()) and base==prop, [mp,base,prop])
        ERRL.extend(errs()); print('     erros JS (ajustes2):',ERRL[:3])
    else:   # icones
        D=json.load(open(os.path.join(HERE,'_icones.json'))) if os.path.exists(os.path.join(HERE,'_icones.json')) else None
        import engine as E
        SAT,MON,LEAF,ALERT,GRID=E.ICONS['satelite'],E.ICONS['monitoramento'],E.ICONS['leaf'],E.ICONS['alert'],E.ICONS['grid']
        TRI="[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')]"
        def trilha(): return c.js(f"{TRI}.map(b=>[b.innerText.replace(/\\s+/g,' ').trim(), b.getAttribute('title'), (b.querySelector('svg path')||{{getAttribute:()=>''}}).getAttribute('d'), Math.round((b.querySelector('svg')||{{getBoundingClientRect:()=>({{width:0}})}}).getBoundingClientRect().width), b.querySelector('svg')&&b.querySelector('svg').getAttribute('aria-hidden')])")
        abre('IN-04',1440,900); t=trilha(); by={x[0]:x for x in t}
        chk('20 trilha do mapa · Satélite = satélite com corpo e painéis; Pragas e doenças = lupa sobre folha; diferentes da folha da Lavoura e do triângulo de alerta; 20 px, aria-hidden, rótulos e títulos mantidos',
            by['Satélite'][2]==SAT and by['Pragas e doenças'][2]==MON and by['Lavoura'][2]==LEAF and len({SAT,MON,LEAF,ALERT,GRID})==5 and by['Satélite'][3]==20 and by['Pragas e doenças'][3]==20
            and by['Satélite'][4]=='true' and by['Satélite'][1]=='Mostrar Satélite no mapa' and by['Pragas e doenças'][1]=='Mostrar Pragas e doenças no mapa', {k:(v[0],v[1],v[3],v[2][:20]) for k,v in by.items()})
        # 21 · painel Integrado de um talhão: "Ver satélite" e "Ver pragas e doenças" com os mesmos desenhos; alerta continua para estado real
        c.js("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); s.value='Santa Rita'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.5)
        c.js("document.querySelector('polygon[role=button]').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); time.sleep(.5)
        hub=c.js(f"(()=>{{const bs=[...document.querySelectorAll('main aside[aria-label] button, main aside[aria-label] a')]; const f=t=>bs.find(b=>b.innerText.trim()===t); const d=b=>b?[...b.querySelectorAll('svg path')].map(p=>p.getAttribute('d')):null; return {{sat:d(f('Ver satélite')), mip:d(f('Ver pragas e doenças')), lav:d(f('Ver lavoura')), }};}})()"); shot('IN-04_1440_painel_icones')
        import re as _re
        BASE_ENG=os.path.join(HERE,'..','..','base_v42','gen37','engine.py'); ab=_re.search(r"'alert':'([^']+)'",open(BASE_ENG).read()).group(1) if os.path.exists(BASE_ENG) else None
        c.js(f"{TRI}.find(b=>b.innerText.trim()==='Pragas e doenças').click()"); time.sleep(.4)
        hub['alerta']=c.js(f"[...document.querySelectorAll('main svg path')].filter(p=>p.getAttribute('d')==={json.dumps(ALERT)}&&p.getClientRects().length).length"); hub['alertaIgualBase']=(ab==ALERT)
        c.js(f"{TRI}.find(b=>b.innerText.trim()==='Integrado').click()"); time.sleep(.3)
        chk('21 painel do talhão · "Ver satélite" e "Ver pragas e doenças" com satélite e lupa sobre folha (um ícone cada); "Ver lavoura" segue com a folha; triângulo de alerta igual à base e ainda em uso (sem troca global)',
            hub['sat']==[SAT] and hub['mip']==[MON] and hub['lav']==[LEAF] and hub['alerta']>0 and hub['alertaIgualBase'], hub)
        # 22 · teclado e clique abrem a camada certa e conservam o talhão e a fazenda
        c.js(f"{TRI}.find(b=>b.innerText.trim()==='Satélite').focus()"); c.tecla('Enter','Enter',13,text='\r'); time.sleep(.5)
        s1=c.js(f"(()=>{{const b={TRI}.find(b=>b.innerText.trim()==='Satélite'); const a=document.querySelector('main aside[aria-label]'); return [b.getAttribute('aria-selected'), a?a.getAttribute('aria-label'):'', document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value, b.matches(':focus-visible'), getComputedStyle(b).outlineStyle];}})()")
        c.js(f"{TRI}.find(b=>b.innerText.trim()==='Pragas e doenças').click()"); time.sleep(.5)
        s2=c.js(f"(()=>{{const b={TRI}.find(b=>b.innerText.trim()==='Pragas e doenças'); const a=document.querySelector('main aside[aria-label]'); const l=[...document.querySelectorAll('main a')].find(x=>x.innerText.trim().startsWith('Abrir monitoramento')); return [b.getAttribute('aria-selected'), a?a.getAttribute('aria-label'):'', !!l, getComputedStyle(b).backgroundColor, getComputedStyle(b).color];}})()"); shot('IN-04_1440_pragas_selecionado')
        chk('22 teclado (Enter) abre Satélite com foco visível; clique abre Pragas e doenças (selecionado verde com ícone branco) e "Abrir monitoramento"; talhão e fazenda conservados',
            s1[0]=='true' and s1[1].startswith('T1') and s1[2]=='Santa Rita' and s1[3] and s1[4]=='solid' and s2[0]=='true' and s2[1].startswith('T1') and s2[2] and s2[3]=='rgb(30, 107, 71)' and s2[4]=='rgb(255, 255, 255)', [s1,s2])
        # 23 · estados da trilha: hover (camada interna) ≠ selecionado (fundo verde) ≠ foco (contorno); celular: rótulos visíveis e nome acessível
        TB=f"{TRI}.find(b=>b.innerText.trim()==='Satélite')"
        xy=centro(TB); c.mouse(*xy); time.sleep(.15); hv=estilo(TB,['box-shadow','background-color','outline-style']); c.mouse(5,890); time.sleep(.1)
        abre('IN-04',360,800,3,True); tc=trilha(); shot('IN-04_360x800_trilha')
        chk('23 trilha · hover = camada interna sem trocar o fundo; no celular (360 px) Satélite e Pragas e doenças com rótulo visível, título e os novos desenhos',
            'inset' in hv[0] and hv[1] in ('rgba(0, 0, 0, 0)','transparent') and any(x[0]=='Satélite' and x[2]==SAT and x[1] for x in tc) and any(x[0]=='Pragas e doenças' and x[2]==MON and x[1] for x in tc), [hv,[(x[0],x[1]) for x in tc][:4]])
        # 24 · capturas antes/depois da trilha (desktop e celular) e menu recolhido com nome acessível
        AD=os.environ.get('ANTES_DIR') or next((d for d in (os.path.join(HERE,'..','..','base_v42','gen37','_render'),os.path.join(HERE,'..','gen37_antes','_render')) if os.path.isdir(d)),None)
        def recorte(nome):
            r=c.js("(()=>{const n=document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"]'); n.scrollIntoView({block:'start'}); const b=n.getBoundingClientRect(); return [b.left,b.top,b.width,Math.min(b.height,innerHeight-b.top)];})()")
            import base64; d=c.call('Page.captureScreenshot',{'format':'png','clip':{'x':r[0],'y':r[1],'width':r[2],'height':r[3],'scale':2}}); open(os.path.join(PROBE,f'comp_{nome}.png'),'wb').write(base64.b64decode(d['data']))
        c.js("sessionStorage.removeItem('mapa-ctx')"); abre('IN-04',1440,900); recorte('icones_depois_1440'); abre('IN-04',360,800,3,True); recorte('icones_depois_360')
        antes=False
        if AD:
            p2,s2=servir(AD)
            try:
                c.aparelho(1440,900); c.goto(f'http://127.0.0.1:{p2}/IN-04.dc.html',.6); recorte('icones_antes_1440'); c.aparelho(360,800,3,True); c.goto(f'http://127.0.0.1:{p2}/IN-04.dc.html',.6); recorte('icones_antes_360'); antes=True
            finally: s2.terminate()
        abre('IN-04',1440,900,rec='1'); rc=c.js("[...document.querySelectorAll('.menu-lat a,.menu-lat>button')].filter(e=>e.getClientRects().length).map(e=>[e.getAttribute('title')||e.getAttribute('aria-label')||'', Math.round(e.getBoundingClientRect().width)])")
        chk('24 capturas antes/depois da trilha (1440 e 360 px) gravadas; menu da casca recolhido: todo item visível tem nome (título)', antes and all(x[0] for x in rc), [antes,AD,rc])
        ERRL.extend(errs()); chk('25 sem erro de JS nas telas visitadas (ícones)', not ERRL, ERRL[:5])
finally:
    if c: c.close()
    srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas ({MODO})'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)
