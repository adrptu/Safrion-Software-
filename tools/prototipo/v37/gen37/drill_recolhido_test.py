# -*- coding: utf-8 -*-
"""TAB-12 · Drill down recolhido por padrão (proprietário, 17/10/2026: "Por padrão coloque sempre os cartoes e tabelas com drill down
recolhido, primeiro usuario tem a visao macro e depois consegue escolher onde precisar detalhar no drill down expandido. Em todas as telas.";
e, no Planejar safra › etapa 2: "quando so tem 1 fazenda nao agrupa por fazenda, só quando tem 2 ou mais. corrija."). Regra em
docs/design-system/padroes-1610.md § TAB-12 e § TAB-13. Navegador real (Chrome headless), 1440 × 900 e 390 × 844 (toque), dados sintéticos.
A  abertura de todas as páginas do _render (fora Main e redirecionamentos) e dos estados por endereço (EXTRAS):
   A1 tabelas [role=table][data-g2g]: nenhuma seta de abrir (.g2car) com aria-expanded=true e nenhuma linha-filha à vista (a 1ª célula
      da linha-filha tem o recuo do nível, ≥ 28 px);
   A2 cartões (.g2cartoes): nenhuma seta aberta, nenhuma lista de filhos (.g2cd-kids) e, com Agrupar por, nenhum cartão sob título de grupo;
   A3 a tela: nenhum controle com aria-expanded=true nem <details> aberto, fora as exceções da TAB-12: lista suspensa e menu
      ([aria-haspopup], combobox, menu, listbox), campos, raia do Kanban da O.S. (.os-raia-cab) e seção do painel de UM registro
      ([data-secao-registro]); estado por ação mede só o painel que a ação abriu;
   A4 contagem mínima (a varredura viu tabelas em árvore, cartões e setas: rodada vazia não passa);
   G  sem erro de JavaScript e todo estado abriu.
B  amostras por módulo (Planejar safra etapa 2 com 1 e com 2 fazendas, O.S. com Agrupar por, Cadastros CD-01 árvore, Atividades do plano,
   Manutenção, Estoque saldos por lote, Qualidade CO-06), nas duas larguras:
   B1 1 clique na seta abre só aquele item (1 aberto no escopo, o conteúdo dele aparece);
   B2 Enter e Espaço na seta, com o foco nela, abrem e recolhem (1 aberto, depois nenhum);
   B3 "Expandir tudo" abre todos os do escopo e "Recolher tudo" recolhe (onde a tela tem o botão);
   B4 a linha recolhida mostra o resumo: a faixa da fazenda diz a área e os talhões planejados; o total da tabela não muda ao expandir.
D  TAB-13 (proprietário, 17/10/2026, print da O.S. › Tabela agrupada por Talhão: "o simbolo de drill down so deve aparecer onde de fato terá um
   detalhamento drill down"), em todas as páginas e estados de A, na abertura e com "Expandir tudo":
   D1 nenhuma seta de ir (.g2drill) e nenhuma seta fora de controle de abrir (botão com aria-expanded, summary) ou do "Expandir tudo";
   D2 toda seta aberta tem o que mostrar: linha filha logo abaixo (tabela), lista de filhos com itens (cartão), cartões (grupo dos cartões).
C  exceções que continuam abrindo:
   C1 busca que acha um talhão (T3) abre o caminho até ele (faixa da fazenda); limpar a busca volta a recolher;
   C2 endereço de um registro dentro de grupo (PROD.dc.html#<lote>) abre só o caminho dele e mostra a linha.
Contraprova: RENDER_DIR=<render da 7d65025> reprova A1/A2/A3 e B (abria por padrão) e D1 (seta de ir nas linhas folha).
Uso (de gen37/): CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B drill_recolhido_test.py · DRT_LARG=1440 ou 390 (padrão: as duas)
· DRT_SO=CD-01,SAF (diagnóstico de poucas telas; a contagem mínima faz a rodada parcial reprovar: não vale como prova).
Saída: uma linha por desvio (até 30 por regra) e o RESULTADO; sai 1 se falhar."""
import os, sys, json, glob, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from areas.maquinas import REDIRECIONA

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
LARGS = [int(x) for x in (os.environ.get('DRT_LARG') or '1440,390').split(',')]
FORA = set(REDIRECIONA) | {'Main.dc.html'}
PAGS = sorted(os.path.basename(f) for f in glob.glob(os.path.join(R, '*.dc.html')) if os.path.basename(f) not in FORA)
# estados por endereço (painel ou plano aberto, visão, agrupamento) e por ação (ajuste local do Planejar safra: mede só o painel)
EXTRAS = ['PA.dc.html#plano=SOJA-AT', 'PA.dc.html?view=tabela#plano=SOJA-AT', 'SAF.dc.html#saf=S2627&passo=cultivos', 'SAF.dc.html#saf=S2627&passo=operacoes',
          'SAF.dc.html#saf=S27SF&passo=cultivos', 'MA.dc.html#ativo=a01', 'MA.dc.html#om=OM-0233', 'MA.dc.html#plano=PM-01', 'OS.dc.html#OS-0420',
          'OS.dc.html?view=lista&ag=onde', 'OS.dc.html?view=kanban&ag=onde', 'AG-02.dc.html#LAU-2073', 'CD-01.dc.html?view=cartoes',
          'SAF.dc.html#saf=S2627&passo=cultivos|ajuste']
SO = [x for x in (os.environ.get('DRT_SO') or '').split(',') if x]   # diagnóstico: só as telas cujo endereço contém um destes trechos
if SO: PAGS, EXTRAS = [p for p in PAGS if any(x in p for x in SO)], [p for p in EXTRAS if any(x in p for x in SO)]
OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:1500]), flush=True)

VIS = "const vis=e=>{ if(!e||!e.getBoundingClientRect) return false; const r=e.getBoundingClientRect(); if(r.width<=1||r.height<=1) return false; const cs=getComputedStyle(e); return cs.visibility!=='hidden'&&cs.display!=='none'; }; const N=s=>(s||'').replace(/\\s+/g,' ').trim().slice(0,48);"
# esc: seletor do escopo de A3 ('' = a página toda; no estado por ação, o painel aberto)
MEDE = r"""((esc)=>{ %s
 const out={a1:[],a2:[],a3:[],nT:0,nArv:0,nC:0,nSeta:0,nLin:0};
 const raiz=esc?[...document.querySelectorAll(esc)].filter(vis).pop():document;
 if(!esc){
  for(const t of [...document.querySelectorAll('[role=table][data-g2g]')].filter(vis)){ out.nT++; const g=t.getAttribute('data-g2g');
    const setas=[...t.querySelectorAll('button.g2car[aria-expanded]')].filter(vis); if(setas.length) out.nArv++; out.nSeta+=setas.length;
    setas.filter(b=>b.getAttribute('aria-expanded')==='true').forEach(b=>out.a1.push(g+' seta aberta «'+N(b.getAttribute('aria-label'))+'»'));
    for(const r of [...t.querySelectorAll('[role=row][data-rid]')].filter(vis)){ out.nLin++; const c0=r.querySelector('.g2c0'); const pl=c0?parseFloat(c0.style.paddingLeft||'0'):0;
      if(pl>=27.5) out.a1.push(g+' linha-filha à vista «'+N(r.innerText)+'»'); } }
  for(const k of [...document.querySelectorAll('.g2cartoes[data-g2cd]')].filter(vis)){ out.nC++; const g=k.getAttribute('data-g2cd');
    [...k.querySelectorAll('[aria-expanded=true]')].filter(vis).forEach(b=>out.a2.push(g+' seta aberta «'+N(b.getAttribute('aria-label'))+'»'));
    [...k.querySelectorAll('.g2cd-kids')].filter(vis).forEach(x=>out.a2.push(g+' filhos à vista «'+N(x.getAttribute('aria-label'))+'»'));
    if([...k.querySelectorAll('.g2cd-gcab')].some(vis)) [...k.querySelectorAll('[role=listitem].g2cd')].filter(vis).slice(0,3).forEach(x=>out.a2.push(g+' cartão sob grupo recolhido «'+N(x.innerText)+'»')); } }
 const FORA='[aria-haspopup],[role=combobox],[role=menu],[role=listbox],input,select,textarea,.os-raia-cab,[data-secao-registro]';
 for(const e of (raiz?[...raiz.querySelectorAll('[aria-expanded=true],details[open]')]:[]).filter(vis)){ if(e.matches(FORA)||e.closest('[role=menu],[role=listbox]')) continue;
   if(!esc&&e.closest('[role=table][data-g2g],.g2cartoes[data-g2cd]')) continue;   // já em A1/A2
   out.a3.push(e.tagName.toLowerCase()+(typeof e.className==='string'&&e.className.trim()?'.'+e.className.trim().split(/\s+/)[0]:'')+' «'+N(e.getAttribute('aria-label')||e.innerText)+'»'); }
 return out; })""" % VIS
# TAB-13 · seta só onde há o que abrir (todo estado): D1 nenhuma seta de ir (.g2drill) nem seta solta, fora de controle de abrir (botão com
# aria-expanded, summary) ou do "Expandir tudo"; D2 toda seta aberta tem o que mostrar: na tabela, a linha seguinte é de nível mais fundo; no
# cartão, a lista de filhos com itens; no grupo dos cartões, cartões embaixo (com "Expandir tudo" quase toda seta fica aberta: a prova é aí)
MEDE_D = r"""(()=>{ %s
 const out={d1:[],d2:[],nAb:0};
 for(const s of [...document.querySelectorAll('.g2seta')].filter(vis)){ const dono=s.closest('button[aria-expanded],summary,.g2xtog');
   if(s.classList.contains('g2drill')||!dono) out.d1.push((s.classList.contains('g2drill')?'seta de ir':'seta solta')+' «'+N((s.closest('[role=row],[role=listitem],button,a,li')||s.parentElement).innerText)+'»'); }
 const nivel=r=>{ const c0=r.querySelector('.g2c0'); const pl=c0?parseFloat(c0.style.paddingLeft||'8'):8; return Math.round((pl-8)/20); };
 for(const t of [...document.querySelectorAll('[role=table][data-g2g]')].filter(vis)){ const rs=[...t.querySelectorAll('[role=row][data-rid]')].filter(vis);
   rs.forEach((r,i)=>{ const b=[...r.querySelectorAll('button.g2car[aria-expanded=true]')].find(vis); if(!b) return; out.nAb++;
     const prox=rs[i+1]; if(!prox||nivel(prox)<=nivel(r)) out.d2.push(t.getAttribute('data-g2g')+' seta aberta sem linha filha «'+N(r.innerText)+'»'); }); }
 for(const k of [...document.querySelectorAll('.g2cartoes[data-g2cd]')].filter(vis)){
   for(const cd of [...k.querySelectorAll('[role=listitem].g2cd')].filter(vis)){ const b=cd.querySelector(':scope>.g2cd-lin button.g2car[aria-expanded=true]'); if(!b||!vis(b)) continue; out.nAb++;
     const ks=cd.querySelector(':scope>sc-if>.g2cd-kids,:scope>.g2cd-kids'); if(!ks||![...ks.querySelectorAll('[role=listitem]')].some(vis)) out.d2.push(k.getAttribute('data-g2cd')+' cartão aberto sem filhos «'+N(cd.innerText)+'»'); }
   for(const h of [...k.querySelectorAll('.g2cd-gcab')].filter(vis)){ const b=h.querySelector('button.g2car[aria-expanded=true]'); if(!b||!vis(b)) continue; out.nAb++;
     let n=h.closest('sc-if')||h; let g=n.nextElementSibling; const tem=!!g&&[...g.querySelectorAll('[role=listitem].g2cd')].some(vis); if(!tem) out.d2.push(k.getAttribute('data-g2cd')+' grupo aberto sem cartões «'+N(h.innerText)+'»'); } }
 return out; })()""" % VIS
XTOG = "(()=>{ const bs=[...document.querySelectorAll('button.g2xtog')].filter(b=>b.getClientRects().length&&/Expandir/.test(b.innerText)); bs.forEach(b=>b.click()); return bs.length; })()"
# ajuste local do Planejar safra: a pessoa abre a faixa (Expandir tudo), a linha do cultivo e "Ajustar insumos e doses de …"
AJUSTE = r"""(async ()=>{ const vis=e=>!!e&&e.getClientRects().length>0, N=s=>(s||'').replace(/\s+/g,' ').trim(), espera=ms=>new Promise(r=>setTimeout(r,ms));
 [...document.querySelectorAll('button.g2xtog')].filter(b=>vis(b)&&/Expandir/.test(b.innerText)).forEach(b=>b.click()); await espera(500);
 for(const t of ['T7','T3','T2','T4','T5','T6']){ const row=[...document.querySelectorAll('[role=row].g2ed')].filter(vis).find(r=>new RegExp('^'+t+'\\b').test(N(r.innerText))); if(!row) continue;
   (row.querySelector('.g2pw')||row).click(); await espera(500);
   const b=[...document.querySelectorAll('aside[role=dialog] button')].filter(vis).find(x=>/^(Ajustar|Ver) insumos e doses de /.test(N(x.innerText))); if(b){ b.click(); await espera(600); return 'ok'; } }
 return 'sem ação de insumos em T7, T3, T2, T4, T5, T6'; })()"""
ESC_ACAO = {'ajuste': 'aside[role=dialog]'}

def varre(c, J, BASE, w):
    res = {'a1': [], 'a2': [], 'a3': [], 'd1': [], 'd2': [], 'err': []}; telas = {k: set() for k in res}; n = {'nT': 0, 'nArv': 0, 'nC': 0, 'nSeta': 0, 'nLin': 0, 'nAb': 0, 'nXt': 0}
    for pg in PAGS + EXTRAS:
        url, acao = (pg.split('|') + [''])[:2]
        c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.1); c.goto(BASE + url, 1.0)
        esc = ''
        if acao:
            r = J(AJUSTE)
            if r != 'ok': res['err'].append((w, pg, acao + ': ' + str(r))); telas['err'].add(pg)
            esc = ESC_ACAO[acao]
        m = J(f"{MEDE}({json.dumps(esc)})") or {}
        for k in n: n[k] += m.get(k, 0)
        for k in ('a1', 'a2', 'a3'):
            for x in m.get(k) or []: res[k].append((w, pg, x)); telas[k].add(pg)
        d = J(MEDE_D) or {}
        if not acao and J(XTOG): n['nXt'] += 1; time.sleep(.7); d2 = J(MEDE_D) or {}; d = {'d1': (d.get('d1') or []) + (d2.get('d1') or []), 'd2': d2.get('d2') or [], 'nAb': d2.get('nAb', 0)}
        n['nAb'] += d.get('nAb', 0)
        for k in ('d1', 'd2'):
            for x in dict.fromkeys(d.get(k) or []): res[k].append((w, pg, x)); telas[k].add(pg)
        for e in (J("window.__errs||[]") or [])[:2]: res['err'].append((w, pg, str(e)[:160])); telas['err'].add(pg)
        J("try{localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')}catch(e){}")
    return res, telas, n

# ---------- B · amostras por módulo ----------
# escopo, seta e o que a tela oferece; prep: passos antes de medir (JS ou função Python)
ESPERA_TAB = "(()=>!!document.querySelector('[role=table]'))()"
def prep_secao(i): return f"(()=>{{ const b=document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[{i - 1}]; if(b) b.click(); return !!b; }})()"
def prep_boa_vista(c, J):   # inclui a Boa Vista na safra (SAF-FAZ-3): a tabela passa a ter duas faixas de fazenda
    J("document.getElementById('sfz-add')&&document.getElementById('sfz-add').click()"); espera(J, "!!document.getElementById('sfz-pop')")
    J("(()=>{ const l=[...document.querySelectorAll('#sfz-pop label')].find(l=>l.querySelector('b')&&l.querySelector('b').innerText.trim()==='Boa Vista'); if(l) l.querySelector('input').click(); })()")
    ok = espera(J, "/Boa Vista entrou/.test(document.body.innerText)")
    c.tecla('Escape', 'Escape', 27); espera(J, "!document.getElementById('sfz-pop')")
    return ok and espera(J, "document.querySelectorAll('[role=table][data-g2g=\"g_cult_S27SF\"] [role=row][data-rid^=\"fzg_\"]').length===2")
AMOSTRAS = [
    dict(id='SAF1', nome='Planejar safra › etapa 2 · 1 fazenda', url='SAF.dc.html?r=1#saf=S2627&passo=cultivos', esc='[role=table][data-g2g="g_cult_S2627"]',
         seta='button.g2car[aria-expanded]', xtog=True, faixa=1),
    dict(id='SAF2', nome='Planejar safra › etapa 2 · 2 fazendas', url='SAF.dc.html?r=2#saf=S27SF&passo=cultivos', esc='[role=table][data-g2g="g_cult_S27SF"]',
         seta='button.g2car[aria-expanded]', xtog=True, faixa=2, prep=prep_boa_vista),
    dict(id='OS', nome='Ordem de Serviço · Tabela com Agrupar por', url='OS.dc.html?view=lista&ag=onde', esc='[role=table][data-g2g="g_os"]', seta='button.g2car[aria-expanded]', xtog=True),
    dict(id='CD01', nome='Cadastros CD-01 · fazendas e talhões (árvore)', url='CD-01.dc.html', esc='[role=table][data-g2g="g_tal"]', seta='button.g2car[aria-expanded]', xtog=True),
    dict(id='PA', nome='Atividades do plano (Tabela)', url='PA.dc.html?view=tabela#plano=SOJA-AT', esc='main', seta='button.g2car[aria-controls]', xtog=True),
    dict(id='MA', nome='Manutenção · blocos do ativo', url='MA.dc.html#ativo=a01', esc='main', seta='button.ma-blh[aria-expanded]', xtog=False),
    dict(id='EST', nome='Estoque · saldos por lote (seção 4)', url='EST.dc.html', esc='[role=table][data-g2g="g_lot"]', seta='button.g2car[aria-expanded]', xtog=True, prep=prep_secao(4)),
    dict(id='CO06', nome='Qualidade CO-06 · lotes', url='CO-06.dc.html', esc='main', seta='button[aria-controls="car-det"][aria-expanded]', xtog=False),
]
def espera(J, expr, lim=6.0):
    fim = time.monotonic() + lim
    while time.monotonic() < fim:
        try:
            if J('(()=>{try{return !!(' + expr + ')}catch(e){return false}})()'): return True
        except Exception: pass
        time.sleep(.1)
    return False
def estado(J, a):   # setas do escopo: [aria-expanded], rótulo; tamanho do texto da área principal (o conteúdo aberto aparece)
    return J("(()=>{ %s const E=[...document.querySelectorAll(%s)].filter(vis).pop(); if(!E) return null;"
             " const S=[...E.querySelectorAll(%s)].filter(vis); const m=document.querySelector('main')||document.body;"
             " return {n:S.length, ab:S.filter(b=>b.getAttribute('aria-expanded')==='true').map(b=>N(b.getAttribute('aria-label')||b.innerText)), lab0:S[0]?N(S[0].getAttribute('aria-label')||S[0].innerText):'',"
             " txt:(m.innerText||'').length, tot:((E.querySelector('.g2tot')||{}).innerText||'').replace(/\\s+/g,' ').trim(),"
             " faixas:[...E.querySelectorAll('[role=row][data-rid^=\"fzg_\"]')].filter(vis).map(r=>N(r.innerText))}; })()" % (VIS, json.dumps(a['esc']), json.dumps(a['seta'])))
def abre(c, J, BASE, a, w):
    c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.1); c.goto(BASE + 'Main.dc.html', .2)
    J("try{localStorage.clear();sessionStorage.clear();localStorage.setItem('safrion.perfilDemo','Ana')}catch(e){}")
    c.goto(BASE + a['url'], 1.2); espera(J, "document.querySelectorAll(%s).length>0" % json.dumps(a['seta']), 8)
    p = a.get('prep')
    if callable(p): return p(c, J)
    if p: J(p); time.sleep(.6); return espera(J, "document.querySelectorAll(%s).length>0" % json.dumps(a['seta']), 6)
    return True
def clica_seta(J, a, i=0):
    return J("(()=>{ %s const E=[...document.querySelectorAll(%s)].filter(vis).pop(); const b=E&&[...E.querySelectorAll(%s)].filter(vis)[%d]; if(!b) return false; b.scrollIntoView({block:'center'}); b.click(); return true; })()"
             % (VIS, json.dumps(a['esc']), json.dumps(a['seta']), i))
def foca_seta(J, a, i=0):
    return J("(()=>{ %s const E=[...document.querySelectorAll(%s)].filter(vis).pop(); const b=E&&[...E.querySelectorAll(%s)].filter(vis)[%d]; if(!b) return false; b.scrollIntoView({block:'center'}); b.focus(); return document.activeElement===b; })()"
             % (VIS, json.dumps(a['esc']), json.dumps(a['seta']), i))
def xtog(J, txt):
    return J("(()=>{ const bs=[...document.querySelectorAll('button.g2xtog')].filter(b=>b.getClientRects().length&&b.innerText.indexOf(%s)>=0); bs.forEach(b=>b.click()); return bs.length; })()" % json.dumps(txt))

def amostras(c, J, BASE, w):
    for a in AMOSTRAS:
        tag = f"B{w} {a['id']}"
        if not abre(c, J, BASE, a, w): chk(f'{tag} preparação ({a["nome"]})', False, 'a tela não chegou ao estado da amostra'); continue
        e0 = estado(J, a) or {}
        # B1 · um clique abre só aquele item
        clica_seta(J, a); time.sleep(.6); e1 = estado(J, a) or {}
        chk(f'{tag} B1 {a["nome"]}: recolhido na abertura ({e0.get("n")} setas, {len(e0.get("ab") or [])} abertas); 1 clique abre só aquele item e o conteúdo dele aparece',
            e0.get('n', 0) >= 1 and not e0.get('ab') and len(e1.get('ab') or []) == 1 and e1.get('txt', 0) > e0.get('txt', 0), [e0.get('n'), e0.get('ab'), e1.get('ab'), e0.get('txt'), e1.get('txt')])
        # B4 · a linha recolhida mostra o resumo
        if a.get('faixa'):
            fx = e0.get('faixas') or []
            chk(f'{tag} B4 faixa da fazenda recolhida com o resumo (área em ha e talhões planejados): {a["faixa"]} faixa(s)',
                len(fx) == a['faixa'] and all(' ha' in x and 'planejad' in x for x in fx), fx)
        # B2 · teclado: Enter abre, Espaço recolhe (reabre a tela para partir do recolhido)
        abre(c, J, BASE, a, w); k0 = estado(J, a) or {}
        fo = foca_seta(J, a)
        c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.5); k1 = estado(J, a) or {}
        foca_seta(J, a); c.tecla(' ', 'Space', 32, text=' '); time.sleep(.5); k2 = estado(J, a) or {}
        chk(f'{tag} B2 Enter na seta abre só aquele item e Espaço recolhe (foco na seta)',
            fo and not k0.get('ab') and len(k1.get('ab') or []) == 1 and not k2.get('ab'), [fo, k0.get('ab'), k1.get('ab'), k2.get('ab')])
        # B3 · Expandir tudo / Recolher tudo; o total não muda com a abertura
        if a['xtog']:
            t0 = (estado(J, a) or {}).get('tot', '')
            nx = xtog(J, 'Expandir tudo'); time.sleep(.7); x1 = estado(J, a) or {}
            ny = xtog(J, 'Recolher tudo'); time.sleep(.7); x2 = estado(J, a) or {}
            chk(f'{tag} B3 "Expandir tudo" abre todas as setas do escopo ({x1.get("n")}) e "Recolher tudo" recolhe; o total não muda',
                nx >= 1 and ny >= 1 and x1.get('n', 0) >= 1 and len(x1.get('ab') or []) == x1.get('n') and not x2.get('ab') and x1.get('tot', '') == t0,
                [nx, ny, x1.get('n'), len(x1.get('ab') or []), x2.get('ab'), t0[:80], x1.get('tot', '')[:80]])

# ---------- C · exceções que continuam abrindo ----------
QSET = r"""((q)=>{ const m=document.querySelector('[data-g2q="g_cult_S2627"]'); const i=m&&m.parentElement.querySelector('input[type=search]'); if(!i) return false;   // a busca da própria tabela
 Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,q); i.dispatchEvent(new Event('input',{bubbles:true})); return true; })"""
def excecoes(c, J, BASE, w):
    a = AMOSTRAS[0]
    abre(c, J, BASE, a, w)
    J(f"{QSET}('T3')"); time.sleep(.7); s1 = estado(J, a) or {}   # T3: talhão inteiro da Santa Rita (folha dentro da faixa)
    vis_t5 = J("[...document.querySelectorAll('[role=table][data-g2g=\"g_cult_S2627\"] [role=row][data-rid]')].filter(r=>r.getClientRects().length).some(r=>/^T3\\b/.test(r.innerText.trim()))")
    J(f"{QSET}('')"); time.sleep(.7); s2 = estado(J, a) or {}
    chk(f'C{w} C1 busca "T3" abre o caminho (faixa da fazenda) e mostra o T3; limpar a busca volta ao recolhido',
        len(s1.get('ab') or []) >= 1 and vis_t5 and not s2.get('ab'), [s1.get('ab'), vis_t5, s2.get('ab')])
    # C2 · endereço de um lote (Produção): só o caminho até ele abre e a linha aparece
    c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.1); c.goto(BASE + 'PROD.dc.html', 1.2)
    xtog(J, 'Expandir tudo'); time.sleep(.6)
    lote = J("(()=>{ const t=document.querySelector('[role=table][data-g2g=\"g_lot\"]'); if(!t) return ''; const r=[...t.querySelectorAll('[role=row][data-rid]')].find(r=>{ const c0=r.querySelector('.g2c0'); return c0&&parseFloat(c0.style.paddingLeft||'0')>=27.5; }); return r?r.getAttribute('data-rid'):''; })()") or ''
    c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.1); c.goto(BASE + 'PROD.dc.html#' + lote, 1.4)
    espera(J, "[...document.querySelectorAll('[role=table][data-g2g=\"g_lot\"] [role=row][data-rid]')].some(r=>r.getAttribute('data-rid')===%s)" % json.dumps(lote), 4)
    if not J("(()=>{ const t=document.querySelector('[role=table][data-g2g=\"g_lot\"]'); return !!t&&t.getClientRects().length>0; })()"):   # no celular o painel do lote cobre a lista: fecha (Esc) e olha a lista
        c.tecla('Escape', 'Escape', 27); time.sleep(.6)
        J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); const b=a&&[...a.querySelectorAll('button')].find(b=>/^(Fechar|Voltar)/.test((b.getAttribute('aria-label')||b.innerText||'').trim())); if(b) b.click(); })()"); time.sleep(.6)
    d = J("(()=>{ %s const t=document.querySelector('[role=table][data-g2g=\"g_lot\"]'); if(!t) return null; const S=[...t.querySelectorAll('button.g2car[aria-expanded]')].filter(vis);"
          " const r=[...t.querySelectorAll('[role=row][data-rid]')].find(x=>x.getAttribute('data-rid')===%s); return {n:S.length, ab:S.filter(b=>b.getAttribute('aria-expanded')==='true').length, linha:!!r&&vis(r)}; })()" % (VIS, json.dumps(lote))) or {}
    chk(f'C{w} C2 endereço do lote {lote or "?"} (PROD.dc.html#…) abre só o caminho dele e mostra a linha', bool(lote) and d.get('linha') and d.get('ab') == 1 and d.get('n', 0) >= 2, [lote, d])

p, srv = servir(R); c = Chrome(); J = c.js; BASE = f'http://127.0.0.1:{p}/'
try:
    for w in LARGS:
        h, e, t = (900, 1, False) if w > 500 else (844, 2, True)
        c.aparelho(w, h, e, t); c.goto(BASE + 'Main.dc.html', .3); J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
        res, telas, n = varre(c, J, BASE, w)
        dd = lambda L: list(dict.fromkeys(L))
        print(f'# {w} px · {len(PAGS)} telas + {len(EXTRAS)} estados · {n["nT"]} tabelas ({n["nArv"]} com seta de abrir; {n["nSeta"]} setas; {n["nLin"]} linhas) · {n["nC"]} listas em cartões', flush=True)
        for k in ('a1', 'a2', 'a3', 'd1', 'd2', 'err'):
            for x in dd(res[k])[:30]: print(f'  {k} ', x, flush=True)
        chk(f'A{w}.1 tabelas: nenhuma seta aberta nem linha-filha à vista na abertura (telas com desvio: {len(telas["a1"])})', not res['a1'], sorted(telas['a1']))
        chk(f'A{w}.2 cartões: nenhuma seta aberta, lista de filhos ou cartão sob grupo na abertura (telas com desvio: {len(telas["a2"])})', not res['a2'], sorted(telas['a2']))
        chk(f'A{w}.3 tela: nenhum controle de abrir aberto nem details aberto, fora as exceções da TAB-12 (telas com desvio: {len(telas["a3"])})', not res['a3'], sorted(telas['a3']))
        # mínimos (rodada completa): medido na candidata a 1440/390: 16/13 tabelas com seta, 92/82 setas, 127/117 abertas com "Expandir tudo"
        chk(f'A{w}.4 a varredura viu tabelas em árvore, setas e cartões (rodada completa)', n['nArv'] >= 10 and n['nSeta'] >= 60 and n['nC'] >= 1 and n['nAb'] >= 100, n)
        chk(f'D{w}.1 TAB-13 nenhuma seta de ir nem seta fora de controle de abrir, na abertura e com "Expandir tudo" (telas com desvio: {len(telas["d1"])})', not res['d1'], sorted(telas['d1']))
        chk(f'D{w}.2 TAB-13 com "Expandir tudo" ({n["nXt"]} telas), toda seta aberta tem o que mostrar ({n["nAb"]} setas abertas; telas com desvio: {len(telas["d2"])})', n['nAb'] >= 100 and not res['d2'], sorted(telas['d2']))
        chk(f'G{w} sem erro de JavaScript e todo estado abriu', not res['err'], res['err'][:6])
        amostras(c, J, BASE, w)
        excecoes(c, J, BASE, w)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas' + (' · ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
