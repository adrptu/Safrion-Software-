# -*- coding: utf-8 -*-
"""NAV-1 · Planos agronômicos sem etapas falsas (lista → detalhe) e o link do cultivo para o Planejar safra (X-AGR-6).
Aceite do docs/navegacao/CONSOLIDADO.md §3.1 e do design system de 09/10 (BOT-01..06, SEL-02, VIS-04), no Chrome headless:
  L1  sem faixa de etapas (.etp-ind) e sem "impedida", na lista e no detalhe
  L2  lista: um cartão por plano; o único verde é "Criar plano", no cabeçalho, à direita do título (BOT-01/02/03/05)
  L3  cartão → detalhe com #plano=SOJA-AT; sem rascunho, nenhuma primária; "‹ Biblioteca de planos" no Próximo passo; Atividades,
      Cultivos e Versões visíveis; "Incluir atividade" branco e compacto no cabeçalho do bloco Atividades, com "+"
  L4  F5 reabre o mesmo plano; #plano=XYZ abre a lista, sem erro; trocar o endereço para #plano=MILHO-SF abre o Milho
  L5  mudar uma dose na tabela: UMA primária "Publicar versão v7"; o resumo das alterações na nota, ao lado dela e NA TELA
      (1440 × 900 aqui; 390 × 844 em L11); "Ver alterações" leva ao bloco completo, o último antes do Próximo passo
  L6  repetição: 2ª mudança no mesmo rascunho v7; publicar: v7 em vigor, sem primária, cultivos "Na v6 · v7 publicada" com o link
      ao cultivo no Planejar safra (#saf=S2627&passo=cultivos&cult=c1)
  L7  erro e recusa: dose 0 recusada sem criar rascunho; inclusão de insumo aberta desabilita Publicar com o motivo; plano novo em
      branco: Publicar desabilitado com o motivo; nome repetido na cultura recusado
  L8  o link abre o Planejar safra na etapa 2 com o painel do cultivo c1 (T1-A)
  L9  teclado: Tab chega ao cartão, Enter abre; Esc fecha o painel e devolve o foco a "Incluir atividade"; Esc (sem painel) volta
      à lista com o foco no cartão aberto
  L10 voltar devolve a posição de rolagem da biblioteca e o foco no último cartão aberto (1440 × 900)
  L11 390 px (toque): sem rolagem lateral; "Criar plano" na tela; mudar a dose e publicar com a primária na tela
  L12 cliques para "mudar uma dose e publicar" (abrir o plano, abrir a atividade, tocar a dose, digitar 0,6 + Enter, publicar):
      medidos na execução real; com ANTES=<_render da base> mede também a base cdc185f no mesmo cenário (1 a menos)
  Revisão adversarial do Codex (09/10), um caso por achado, com a reprodução dele:
  L14 R1/R2: dose digitada sem Enter e clique de verdade em "Publicar" não publica: o botão fica desabilitado com o motivo enquanto
      a dose está aberta; a dose válida entra no rascunho e no resumo ao lado do botão, e só o clique seguinte publica; a dose 0
      sem Enter não publica e o erro continua no campo
  L15 R3: rascunho que volta a ficar igual à v6 desabilita "Publicar" com o motivo
  L16 R4: trocar o endereço com o painel da atividade aberto não troca de plano (endereço volta) nem grava em outro plano
  L17 R6: Esc com o filtro de coluna aberto fecha só o filtro, a 1440 e a 390 px (toque); a 390 px a barra lateral fica recolhida
      (68 px, sem expandir: proprietário, 13/10/2026; antes: Esc com o menu sobreposto fechava só o menu)
  L18 R7: plano novo e F5: o aviso não mostra o id interno
  L19 R8: voltar ou trocar de plano com a inclusão de insumo digitada avisa ("Descartar e …" ou "Continuar editando")
  L13 sem erro de JavaScript
Uso (de gen37/): python3 pa_lista_test.py           (RENDER_DIR=<outro _render> roda contra outro build; sai 1 se falhar)
                 ANTES=<_render da base> python3 pa_lista_test.py   (inclui a medida da base em L12)
Emulação no Chrome headless; não é aparelho físico."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from contextlib import contextmanager
import dados2 as D2
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render'); ANTES = os.environ.get('ANTES') or ''
PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True)
OK = []; FAIL = []
def chk(nome, cond, info=''):
    (OK if cond else FAIL).append(nome); print(('OK   ' if cond else 'FALHA'), nome, ('' if cond else str(info)[:1500]), flush=True)
@contextmanager
def secao(nome):
    """um trecho que quebra (ex.: na base, sem o endereço #plano=) vira falha nomeada e o roteiro segue para o próximo trecho"""
    try: yield
    except Exception as ex: chk(nome + ' · o roteiro não chegou ao fim do trecho', False, repr(ex)[:300])
def info(t, v): print('     (informativo)', t, str(v)[:900], flush=True)
p, srv = servir(R); p0, srv0 = (servir(ANTES) if ANTES else (None, None)); c = None; ERRL = []
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
# estado de comandos: primárias verdes visíveis (cabeçalho e conteúdo), área do Próximo passo, faixa, blocos
EST = r"""(()=>{const n=s=>(s||'').replace(/\s+/g,' ').trim(); const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
 const verde=e=>getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)';
 const prims=[...document.querySelectorAll('header button,header a,main button,main a')].filter(e=>vis(e)&&verde(e)&&!e.closest('.menu-lat')&&!e.closest('[aria-pressed]')&&e.getAttribute('aria-pressed')===null).map(e=>({t:n(e.innerText),cab:!!e.closest('header'),dis:!!e.disabled,why:e.title||''}));
 const a=document.querySelector('[data-acoes]'); const area=a&&vis(a)?[...a.querySelectorAll('button,a,.acoes-nota')].filter(vis).map(e=>(e.dataset.acao||'nota')+':'+n(e.innerText)):[];
 const tit=[...document.querySelectorAll('main h3')].filter(vis).map(h=>n(h.innerText));
 return {prims, area, rot:a?a.getAttribute('aria-label'):'', faixa:!!document.querySelector('.etp-ind,.etp'), impedida:/impedid/i.test(document.body.innerText), tit, hash:location.hash,
   h2:n((document.querySelector('main h2')||{}).innerText||''), cards:document.querySelectorAll('main .g2card').length, dialogo:!!document.querySelector('aside[role=dialog]')};})()"""
def J(x): return c.js(x)
def est(): return J(EST)
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def errs(): return [e for e in (J("window.__errs||[]") or []) if "reading 'g2toast'" not in e]
def abre(url, w=1440, h=900, e=1, t=False, porta=None, limpa=True, espera=.7):
    if c.alvo: ERRL.extend(errs())
    c.aparelho(w, h, e, t); base = f'http://127.0.0.1:{porta or p}/'
    if limpa: c.goto(base + 'Main.dc.html', .2); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(base + url, espera)
def recarrega():
    """F5 de verdade (navegar para o mesmo endereço com âncora não recarrega: é navegação na própria página)"""
    c.call('Page.reload', {'ignoreCache': False}); time.sleep(.6)
    for _ in range(60):
        try:
            if J("document.readyState")=='complete' and J("!!document.body && document.body.innerText.length>50"): break
        except Exception: pass
        time.sleep(.2)
    time.sleep(.6)
def shot(nome): c.shot(os.path.join(PROBE, f'pa_lista_{nome}.png'))
def espera(cond, limite=6.0, passo=.15):
    """espera a condição (expressão JS) ficar verdadeira, até o limite (revisão T1: no lugar das esperas fixas); devolve se ficou"""
    fim = time.time() + limite
    while time.time() < fim:
        try:
            if J(cond): return True
        except Exception: pass
        time.sleep(passo)
    return False
PUB = "document.querySelector('[data-acoes] [data-acao=comando]')"
NOTA = """(()=>{const n=document.querySelector('[data-acoes] .acoes-nota'); const b=document.querySelector('[data-acoes] [data-acao=comando]'); if(!n) return {txt:'',naTela:false,pubNaTela:false,desc:'',dis:!!(b&&b.disabled)};
  const r=n.getBoundingClientRect(), rb=b?b.getBoundingClientRect():null; return {txt:n.innerText.replace(/\\s+/g,' ').trim(), naTela:r.height>0&&r.top>=0&&r.bottom<=innerHeight,
  pubNaTela:!!rb&&rb.top>=0&&rb.bottom<=innerHeight, desc:b?(b.getAttribute('aria-describedby')||''):'', dis:!!(b&&b.disabled)};})()"""
CLIQUES = [0]
def centro(sel, limite=2.0):
    """centro do elemento depois de trazê-lo à tela; espera (até o limite) nada estar por cima dele no ponto do clique, como uma
    lista de busca que ainda está fechando (revisão T1: o clique não cai em outra camada)"""
    fim = time.time() + limite
    while True:
        r = J(f"(()=>{{const e={sel}; if(!e) return null; e.scrollIntoView({{block:'center',inline:'nearest'}}); const r=e.getBoundingClientRect(); const x=r.left+r.width/2, y=r.top+r.height/2; const t=document.elementFromPoint(x,y); return [x,y,!!t&&(e===t||e.contains(t))];}})()")
        if not r or r[2] or time.time() >= fim: return r[:2] if r else None
        time.sleep(.15)
def clique(sel, toque=False, w=.45):
    """clique (ou toque) de verdade no centro do elemento, contado; sel é uma expressão JS que devolve o elemento"""
    xy = centro(sel)
    if not xy: return 'NÃO ACHEI: ' + sel[:80]
    CLIQUES[0] += 1
    if toque: c.toque(*xy)
    else:
        c.mouse(*xy); c.mouse(*xy, 'mousePressed', 'left'); c.mouse(*xy, 'mouseReleased', 'left')
    time.sleep(w); return 'ok'
def btn(txt, raiz='document'): return f"[...{raiz}.querySelectorAll('button,a')].find(b=>b.getClientRects().length&&{N}(b.innerText)==={json.dumps(txt)})"
def btnc(txt, raiz='document'): return f"[...{raiz}.querySelectorAll('button,a')].find(b=>b.getClientRects().length&&{N}(b.innerText).startsWith({json.dumps(txt)}))"
def lab(txt): return f"[...document.querySelectorAll('button')].find(b=>b.getClientRects().length&&(b.getAttribute('aria-label')||'').startsWith({json.dumps(txt)}))"
CARD = lambda nome: f"document.querySelector('main .g2card[aria-label={json.dumps('Abrir plano ' + nome)}]')"
def digita(txt):
    c.call('Input.insertText', {'text': txt}); time.sleep(.15)
def mudar_dose(val, toque=False, abrir=True):
    """Fungicida 1ª aplicação · Fungicida A: abre a atividade (se fechada), toca a dose, digita e confirma com Enter"""
    if abrir and J(f"!!{lab('Mostrar insumos de Fungicida 1ª aplicação')}"): clique(lab('Mostrar insumos de Fungicida 1ª aplicação'), toque)
    clique(lab('Alterar a dose de Fungicida A'), toque, .3)
    J("document.activeElement&&document.activeElement.select&&document.activeElement.select()"); digita(val); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.45)
def publicar_ate(toque=False):
    """anda pelo caminho que a tela oferece até 'Publicar versão v7' (na base passa por 'Revisar e publicar ›') e publica"""
    for _ in range(3):
        if J(f"!!{btnc('Publicar versão v7')}"): break
        if clique("document.querySelector('[data-acoes] [data-acao=avancar]')", toque, .6) != 'ok': break
    return clique(btnc('Publicar versão v7'), toque, .6)
def cenario_cliques(porta, toque=False, w=1440, h=900):
    """mudar uma dose (Fungicida A 0,5 → 0,6 L/ha) e publicar a v7, do índice do menu (lista) até a versão publicada"""
    abre('PA.dc.html', w, h, 3 if toque else 1, toque, porta=porta); CLIQUES[0] = 0
    clique(CARD('Soja alta tecnologia'), toque, .7); mudar_dose('0,6', toque); r = publicar_ate(toque)
    return CLIQUES[0], 3 + 1, r, toast()   # teclas: "0,6" (3) + Enter
try:
    c = Chrome()
    # ---------------- L1-L3 · lista e detalhe sem etapas ----------------
    with secao('L1-L3'):
        abre('PA.dc.html'); l = est(); shot('1440_lista')
        chk('L1a lista sem faixa de etapas e sem "impedida"', not l['faixa'] and not l['impedida'], l)
        criar = J(f"(()=>{{const b={btn('Criar plano')}; if(!b) return null; const cs=getComputedStyle(b); const h1=document.querySelector('header h1').getBoundingClientRect(), r=b.getBoundingClientRect(); return {{cab:!!b.closest('header'), dir:r.left>h1.right, mais:!!b.querySelector('svg'), alt:Math.round(r.height), fs:cs.fontSize}};}})()")
        chk(f'L2 lista: {len(D2.PLANOS)} cartões; o único verde é "Criar plano", no cabeçalho à direita do título, com "+" e tamanho padrão (BOT-01/02/03/04/05); nenhum "Novo plano"',
            l['cards'] == len(D2.PLANOS) and [x['t'] for x in l['prims']] == ['Criar plano'] and l['prims'][0]['cab'] and criar and criar['dir'] and criar['mais'] and criar['fs'] == '14px'
            and not J(f"!!{btn('Novo plano')}") and not l['area'], [l, criar])
        clique(CARD('Soja alta tecnologia'), w=.7); d = est(); shot('1440_detalhe')
        inc = J(f"(()=>{{const b={btn('Incluir atividade')}; if(!b) return null; const s=b.closest('section'); const h=s&&s.querySelector('h3'); const cs=getComputedStyle(b); return {{bg:cs.backgroundColor, fs:cs.fontSize, mais:!!b.querySelector('svg'), bloco:h?h.innerText.trim():'', topo:Math.abs(b.getBoundingClientRect().top-h.getBoundingClientRect().top)<30}};}})()")
        chk('L1b detalhe sem faixa de etapas e sem "impedida"', not d['faixa'] and not d['impedida'], d)
        chk('L3 cartão → detalhe #plano=SOJA-AT; sem rascunho nenhuma primária; Próximo passo só com "‹ Biblioteca de planos"; Atividades, Cultivos e Versões visíveis; "Incluir atividade" branco, compacto, com "+", no cabeçalho do bloco Atividades',
            d['hash'] == '#plano=SOJA-AT' and d['h2'] == 'Soja alta tecnologia' and d['prims'] == [] and d['area'] == ['voltar:‹ Biblioteca de planos'] and d['rot'] == 'Próximo passo'
            and 'Atividades do plano' in d['tit'] and 'Cultivos que usam este plano' in d['tit'] and any(t.endswith('Versões') for t in d['tit'])
            and inc and inc['bg'] == 'rgb(255, 255, 255)' and inc['fs'] == '13px' and inc['mais'] and inc['bloco'] == 'Atividades do plano' and inc['topo'], [d, inc])
    # ---------------- L4 · endereço ----------------
    with secao('L4'):
        recarrega(); f5 = est()
        c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .2); c.goto(f'http://127.0.0.1:{p}/PA.dc.html#plano=XYZ', .8); x = est(); tx = toast(); ex = errs()
        J("location.hash='#plano=MILHO-SF'"); time.sleep(.7); mi = est()
        chk('L4 F5 reabre o mesmo plano; #plano=XYZ abre a lista sem erro (endereço limpo, aviso); trocar o endereço para #plano=MILHO-SF abre o Milho safrinha',
            f5['h2'] == 'Soja alta tecnologia' and f5['hash'] == '#plano=SOJA-AT' and x['cards'] == len(D2.PLANOS) and x['h2'] == '' and x['hash'] == '' and 'não encontrado' in tx and not ex
            and mi['h2'] == 'Milho safrinha', [f5['h2'], x, tx, ex, mi['h2']])
    # ---------------- L5-L6 · mudar a dose, repetição e publicar ----------------
    with secao('L5-L6'):
        abre('PA.dc.html#plano=SOJA-AT'); mudar_dose('0,6'); t1 = toast(); m = est(); shot('1440_rascunho')
        ordem = J(r"""(()=>{const a=document.querySelector('[data-acoes]'); const ss=[...document.querySelectorAll('main section')].filter(s=>s.getClientRects().length); const u=ss[ss.length-1]; if(!a||!u) return {ultimo:'',depois:false,texto:''};
          return {ultimo:(u.querySelector('h3')||{innerText:''}).innerText.trim(), depois:!!(u.compareDocumentPosition(a)&Node.DOCUMENT_POSITION_FOLLOWING), texto:u.innerText.replace(/\s+/g,' ')};})()""")
        nt = J(NOTA); clique(btn('Ver alterações', "document.querySelector('[data-acoes]')"), w=.4)
        alt = J("(()=>{const h=document.getElementById('pa-alt-tit'); if(!h) return null; const r=h.getBoundingClientRect(); return {naTela:r.top>=0&&r.bottom<=innerHeight, foco:document.activeElement===h};})()")
        chk('L5 mudar a dose na tabela: rascunho v7; UMA primária "Publicar versão v7"; o resumo "1 alteração na v7: Fungicida 1ª aplicação (Fungicida A: 0,5 → 0,6 L/ha)." na nota, ao lado dela e na tela a 1440 × 900 (descrição do botão); "Ver alterações" leva ao bloco "Alterações do rascunho v7 em relação à v6" (dose, custo, impacto), o último antes do Próximo passo; cultivos "Continua na v6 ao publicar"',
            'Rascunho v7 criado' in t1 and [x['t'] for x in m['prims']] == ['Publicar versão v7'] and not m['prims'][0]['dis'] and 'comando:Publicar versão v7' in m['area']
            and nt['txt'].startswith('1 alteração na v7: Fungicida 1ª aplicação (Fungicida A: 0,5 → 0,6 L/ha).') and nt['naTela'] and nt['pubNaTela'] and nt['desc'] == 'aa-nota'
            and alt and alt['naTela'] and alt['foco']
            and ordem['ultimo'] == 'Alterações do rascunho v7 em relação à v6' and ordem['depois'] and 'Fungicida A: 0,5 → 0,6 L/ha' in ordem['texto'] and 'Custo de insumos' in ordem['texto'] and 'não serão alterados' in ordem['texto']
            and J("document.querySelector('main').innerText.includes('Continua na v6 ao publicar')"), [t1, m, nt, alt, ordem])
        mudar_dose('0,7', abrir=False); t2 = toast(); m2 = est()
        clique(btn('Publicar versão v7'), w=.7); t3 = toast(); m3 = est(); shot('1440_publicado'); foco = J("(document.activeElement&&document.activeElement.id)||''")
        lk = J("[...document.querySelectorAll('main a')].filter(a=>a.getClientRects().length&&a.innerText.trim()==='Abrir cultivo no Planejar safra ›').map(a=>a.getAttribute('href'))")
        corpo = J("document.querySelector('main').innerText")
        clique(lab('Mostrar as versões'), w=.4); vs = J("(document.getElementById('pa-versoes')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
        chk('L6 repetição: a 2ª mudança fica no rascunho v7 (uma primária); publicar: v7 em vigor e v6 substituída, sem primária nem bloco de alterações; o foco vai aos cultivos; c1, c2, c3 "Na v6 · v7 publicada" com o link ao cultivo no Planejar safra; o aviso e o impacto dizem que a troca de versão ainda não existe no protótipo (R5), sem prometer a adoção',
            'Gravado no rascunho v7' in t2 and [x['t'] for x in m2['prims']] == ['Publicar versão v7'] and 'Versão v7 publicada' in t3 and m3['prims'] == [] and m3['area'] == ['voltar:‹ Biblioteca de planos']
            and not any(t.startswith('Alterações do rascunho') for t in m3['tit']) and corpo.count('Na v6 · v7 publicada') == 3
            and lk == ['SAF.dc.html#saf=S2627&passo=cultivos&cult=c1', 'SAF.dc.html#saf=S2627&passo=cultivos&cult=c2', 'SAF.dc.html#saf=S2627&passo=cultivos&cult=c3']
            and 'v7 publicada em' in vs and 'Em vigor' in vs and 'Substituída' in vs and 'Safra encerrada · fica na v5' in corpo and foco == 'pa-cv-tit'
            and 'No protótipo, a versão publicada aqui ainda não chega ao Planejar safra.' in t3 and 'decida a adoção' not in t3 + corpo and 'no protótipo, ela ainda não existe' in corpo,
            [t2, m2['prims'], t3, m3, lk, vs, corpo.count('Na v6 · v7 publicada'), foco])
    # ---------------- L8 · link ao Planejar safra ----------------
    with secao('L8'):
        clique("[...document.querySelectorAll('main a')].find(a=>a.innerText.trim()==='Abrir cultivo no Planejar safra ›')", w=.2)
        espera("location.pathname.endsWith('SAF.dc.html')&&!![...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length&&/T1-A/.test(x.innerText))", 8)
        sf = J("(()=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const cur=document.querySelector('.etp-ind [aria-current=step]'); const d=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); return {url:location.pathname.split('/').pop()+location.hash, etapa:cur?n(cur.innerText):'', painel:d?n(d.innerText).slice(0,160):''};})()"); shot('1440_saf_cultivo')
        chk('L8 o link abre o Planejar safra na etapa 2 (Cultivos) da 2026/27 com o painel do cultivo c1 (T1-A)',
            sf['url'] == 'SAF.dc.html#saf=S2627&passo=cultivos&cult=c1' and sf['etapa'].startswith('2') and 'T1-A' in sf['painel'], sf)
    # ---------------- L7 · erro e recusa ----------------
    with secao('L7'):
        abre('PA.dc.html#plano=SOJA-AT')
        clique(lab('Mostrar insumos de Fungicida 1ª aplicação')); clique(lab('Alterar a dose de Fungicida A'), w=.3)
        J("document.activeElement.select()"); digita('0'); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.4)
        e0 = J("[...document.querySelectorAll('main [role=alert]')].map(a=>a.innerText.trim()).join(' | ')"); r0 = est()
        c.tecla('Escape', 'Escape', 27); time.sleep(.3); r0b = est()
        clique(lab('Incluir insumo em Fungicida 1ª aplicação'), w=.4); mudar_dose('0,6', abrir=False)   # inclusão aberta + rascunho
        espera(f"!!{PUB}&&!{PUB}.disabled")
        clique(lab('Incluir insumo em Fungicida 1ª aplicação'), w=.1); espera(f"!!{PUB}&&{PUB}.disabled&&!!document.querySelector('[id^=pa-add-dose-]')")
        ia = est(); nota = J("(document.querySelector('[data-acoes] .acoes-nota')||{innerText:''}).innerText.trim()")
        clique(btn('Cancelar', "document.querySelector('main')"), w=.1); espera(f"!document.querySelector('[id^=pa-add-dose-]')&&!!{PUB}&&!{PUB}.disabled"); ib = est()
        chk('L7a dose 0 recusada junto ao campo sem criar rascunho; Esc cancela e o detalhe continua sem primária; com a inclusão de insumo aberta, "Publicar versão v7" desabilitado com o motivo (nota e dica); Cancelar devolve',
            'Informe a dose por hectare, maior que zero.' in e0 and r0['prims'] == [] and r0b['prims'] == [] and r0b['h2'] == 'Soja alta tecnologia'
            and len(ia['prims']) == 1 and ia['prims'][0]['dis'] and ia['prims'][0]['why'] == 'Conclua ou cancele a inclusão do insumo para publicar a v7.' and nota == ia['prims'][0]['why']
            and len(ib['prims']) == 1 and not ib['prims'][0]['dis'], [e0, r0, r0b, ia, nota, ib])
        clique("document.querySelector('[data-acoes] [data-acao=voltar]')", w=.6)
        clique(btn('Criar plano'), w=.5)
        J("(()=>{const s=document.querySelector('#np_cult'); const P=HTMLSelectElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(s,'Soja'); s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
        J("(()=>{const i=document.querySelector('#np_nome'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'soja ALTA tecnologia'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
        rodape = J("[...document.querySelectorAll('aside[role=dialog] .pe-form button')].map(b=>b.innerText.trim())")
        clique(btn('Criar plano', "document.querySelector('aside[role=dialog]')"), w=.4); dup = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText")
        J("(()=>{const i=document.querySelector('#np_nome'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'Soja teste'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
        clique(btn('Criar plano', "document.querySelector('aside[role=dialog]')"), w=.8); nv = est(); nota2 = J("(document.querySelector('[data-acoes] .acoes-nota')||{innerText:''}).innerText.trim()")
        chk('L7b plano novo: rodapé "Cancelar · Criar plano"; nome repetido na cultura recusado; em branco abre o detalhe #plano= com "Publicar versão v1" desabilitado e o motivo; o bloco Atividades mantém "Incluir atividade"',
            rodape == ['Cancelar', 'Criar plano'] and 'Já existe um plano com este nome nesta cultura.' in dup and nv['h2'] == 'Soja teste' and nv['hash'].startswith('#plano=NP')
            and len(nv['prims']) == 1 and nv['prims'][0]['t'] == 'Publicar versão v1' and nv['prims'][0]['dis'] and nota2 == 'Inclua ao menos uma atividade para publicar a v1.'
            and J(f"!!{btn('Incluir atividade')}") and 'Nenhuma atividade ainda' in J("document.querySelector('main').innerText"), [rodape, dup[-200:], nv, nota2])
        clique(btn('Descartar rascunho'), w=.3); clique(btn('Descartar rascunho', "document.querySelector('main [role=alert]')"), w=.6); dsc = est()
        chk('L7c descartar o plano novo volta à lista (sem endereço) e ele sai da biblioteca', dsc['cards'] == len(D2.PLANOS) and dsc['hash'] == '' and 'Plano novo descartado' in toast(), dsc)
    # ---------------- L9 · teclado ----------------
    with secao('L9'):
        abre('PA.dc.html'); J("document.activeElement&&document.activeElement.blur()"); k = 0
        while k < 40 and J("(document.activeElement&&document.activeElement.getAttribute('aria-label'))||''") != 'Abrir plano Soja alta tecnologia': c.tab(); k += 1
        c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.7); k1 = est(); fh = J("(document.activeElement&&document.activeElement.id)||''")
        J(f"{btn('Incluir atividade')}.focus()"); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.5); dl = est()['dialogo'] and J("(document.activeElement&&document.activeElement.id)||''") == 'fm_op'
        c.tecla('Escape', 'Escape', 27); time.sleep(.5); k2 = est(); fv = J(f"document.activeElement==={btn('Incluir atividade')}")
        c.tecla('Escape', 'Escape', 27); time.sleep(.6); k3 = est(); fc = J("(document.activeElement&&document.activeElement.getAttribute('aria-label'))||''")
        chk('L9 teclado: Tab chega ao cartão e Enter abre o detalhe (foco no título do plano); Enter em "Incluir atividade" abre o painel com o foco no 1º campo; Esc fecha e o foco volta ao botão; Esc de novo volta à lista com o foco no cartão aberto',
            k < 40 and k1['hash'] == '#plano=SOJA-AT' and fh == 'pa-det-tit' and dl and not k2['dialogo'] and k2['h2'] == 'Soja alta tecnologia' and fv and k3['cards'] == len(D2.PLANOS) and k3['hash'] == '' and fc == 'Abrir plano Soja alta tecnologia',
            [k, k1['hash'], fh, dl, k2['dialogo'], fv, k3['hash'], fc])
    # ---------------- L10 · posição ----------------
    with secao('L10'):
        abre('PA.dc.html', 1440, 700); ult = J("[...document.querySelectorAll('main .g2card')].pop().getAttribute('aria-label')")
        clique("[...document.querySelectorAll('main .g2card')].pop()", w=.7)
        ROL = "[...document.querySelectorAll('main[data-scroll],.ml-tog+div')].map(e=>Math.round(e.scrollTop))"
        clique("document.querySelector('[data-acoes] [data-acao=voltar]')", w=.7); dep = J(ROL); fcs = J("(document.activeElement&&document.activeElement.getAttribute('aria-label'))||''")
        cur = J("(document.querySelector('main .g2card[aria-current=true]')||{getAttribute:()=>''}).getAttribute('aria-label')")
        chk('L10 "‹ Biblioteca de planos" volta à posição de rolagem da biblioteca, com o foco e a marca no último cartão aberto', max(dep) > 100 and fcs == ult and cur == ult, [dep, fcs, ult, cur])
    # ---------------- L11 · 390 px (toque) ----------------
    with secao('L11'):
        abre('PA.dc.html', 390, 844, 3, True); a = J(r"""(()=>{const b=[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Criar plano'); const r=b?b.getBoundingClientRect():null;
          return {lado:document.documentElement.scrollWidth>innerWidth+1, criar:!!r&&r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight};})()"""); shot('390_lista')
        clique(CARD('Soja alta tecnologia'), True, .8); mudar_dose('0,6', True); n390 = J(NOTA)
        b = J(r"""(()=>{const e=document.querySelector('[data-acoes] [data-acao=comando]'); const r=e?e.getBoundingClientRect():null; const t=r?document.elementFromPoint(r.left+r.width/2,r.top+r.height/2):null;
          return {lado:document.documentElement.scrollWidth>innerWidth+1, prim:e?e.innerText.trim():'', naTela:!!r&&r.top>=0&&r.bottom<=innerHeight&&r.left>=0&&r.right<=innerWidth&&!!t&&e.contains(t)};})()"""); shot('390_rascunho')
        clique("document.querySelector('[data-acoes] [data-acao=comando]')", True, .7); t390 = toast()
        chk('L11 390 px (toque): sem rolagem lateral; "Criar plano" na tela; depois de mudar a dose, "Publicar versão v7" na tela, sem nada por cima, com o resumo das alterações na tela ao lado; publicar pelo toque',
            not a['lado'] and a['criar'] and not b['lado'] and b['prim'] == 'Publicar versão v7' and b['naTela'] and n390['naTela'] and 'Fungicida A: 0,5 → 0,6 L/ha' in n390['txt']
            and 'Versão v7 publicada' in t390, [a, b, n390, t390])
    # ---------------- L12 · cliques medidos (mesmo cenário) ----------------
    with secao('L12'):
        n1, tec1, r1, tt1 = cenario_cliques(p)
        res = {'depois': (n1, tec1, 'Versão v7 publicada' in tt1)}
        if ANTES:
            n0, tec0, r0_, tt0 = cenario_cliques(p0); res['antes cdc185f'] = (n0, tec0, 'Versão v7 publicada' in tt0)
        info('cliques e teclas para mudar uma dose e publicar (cliques, teclas, publicou)', res)
        chk('L12 mudar uma dose e publicar: 4 cliques (abrir o plano, abrir a atividade, tocar a dose, publicar) + "0,6" e Enter; com ANTES, 1 a menos que a base no mesmo cenário',
            res['depois'] == (4, 4, True) and (not ANTES or (res['antes cdc185f'][2] and res['antes cdc185f'][0] - n1 == 1)), res)
    # ---------------- L14 · R1/R2: dose sem Enter e "Publicar" ----------------
    with secao('L14'):
        abre('PA.dc.html#plano=SOJA-AT'); mudar_dose('0,6')
        clique(lab('Mostrar insumos de Dessecação pré-plantio'), w=.3); clique(lab('Alterar a dose de Glifosato 480'), w=.3)
        J("document.activeElement.select&&document.activeElement.select()"); digita('6'); aberta = J(NOTA)
        clique(PUB, w=.1); espera("[...document.querySelectorAll('[role=status]')].some(x=>/entrou no rascunho agora|publicada/.test(x.innerText))", 4)
        t14 = toast(); n14 = J(NOTA); e14 = est(); clique(lab('Mostrar as versões'), w=.3); v14 = J("(document.getElementById('pa-versoes')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
        chk('L14a R1: dose do Glifosato 480 digitada (6) sem Enter: "Publicar" desabilitado com o motivo; o clique de verdade nele não publica: a dose entra no rascunho v7 e no resumo ao lado do botão, o aviso pede para conferir e clicar de novo; a v6 segue em vigor',
            aberta['dis'] and aberta['txt'] == 'Confirme (Enter) ou cancele (Esc) a dose de Glifosato 480 para publicar a v7.'
            and 'Versão v7 publicada' not in t14 and 'A dose de Glifosato 480: 2 → 6 L/ha entrou no rascunho agora' in t14
            and n14['txt'].startswith('2 alterações na v7:') and 'Glifosato 480: 2 → 6 L/ha' in n14['txt'] and 'Fungicida A: 0,5 → 0,6 L/ha' in n14['txt'] and not n14['dis'] and n14['naTela']
            and 'v7 publicada' not in v14 and 'rascunho em edição' in v14, [aberta, t14, n14, v14])
        clique(PUB, w=.1); espera("[...document.querySelectorAll('[role=status]')].some(x=>/Versão v7 publicada/.test(x.innerText))", 4); t14b = toast()
        clique(lab('Mostrar insumos de Dessecação pré-plantio'), w=.3) if J(f"!!{lab('Mostrar insumos de Dessecação pré-plantio')}") else None
        g14 = J(f"(()=>{{const b={lab('Alterar a dose de Glifosato 480')}; return b?b.innerText.trim():'';}})()")
        chk('L14b R1: o clique seguinte publica a v7 com as duas doses que estavam no resumo (Glifosato 480 em 6 L/ha)', 'Versão v7 publicada' in t14b and g14 == '6 L/ha', [t14b, g14])
        abre('PA.dc.html#plano=SOJA-AT'); mudar_dose('0,6'); clique(lab('Alterar a dose de Fungicida A'), w=.3)
        J("document.activeElement.select&&document.activeElement.select()"); digita('0'); clique(PUB, w=.6)
        t2 = toast(); a2 = J("[...document.querySelectorAll('main [role=alert]')].map(a=>a.innerText.trim()).join(' | ')"); n2 = J(NOTA); campo = J("(document.querySelector('input[id^=pa-dose-]')||{value:null}).value")
        chk('L14c R2: dose 0 digitada sem Enter e clique em "Publicar": não publica; o erro continua junto ao campo aberto e o botão segue desabilitado com o motivo',
            'Versão v7 publicada' not in t2 and 'Informe a dose por hectare, maior que zero.' in a2 and campo == '0' and n2['dis'] and n2['txt'].startswith('Confirme (Enter) ou cancele (Esc) a dose de Fungicida A'), [t2, a2, n2, campo])
    # ---------------- L15 · R3: rascunho igual à versão publicada ----------------
    with secao('L15'):
        abre('PA.dc.html#plano=SOJA-AT'); mudar_dose('0,6'); mudar_dose('0,5', abrir=False); n15 = J(NOTA); e15 = est()
        chk('L15 R3: 0,5 → 0,6 → 0,5 deixa o rascunho v7 igual à v6: "Publicar versão v7" desabilitado com o motivo (sem v7 vazia, sem cultivo marcado)',
            len(e15['prims']) == 1 and e15['prims'][0]['dis'] and n15['txt'] == 'O rascunho v7 está igual à v6: altere algo ou descarte o rascunho.' and e15['prims'][0]['why'] == n15['txt'], [n15, e15])
    # ---------------- L16 · R4: endereço trocado com o painel aberto ----------------
    with secao('L16'):
        abre('PA.dc.html#plano=SOJA-AT'); clique("[...document.querySelectorAll('main .pa-editar')].find(b=>b.getClientRects().length)", w=.5)
        p0 = J("(document.querySelector('aside[role=dialog] h2')||{innerText:''}).innerText")
        J("location.hash='#plano=MILHO-SF'"); espera("location.hash==='#plano=SOJA-AT'", 3); time.sleep(.3)
        p1 = J("(document.querySelector('aside[role=dialog] h2')||{innerText:''}).innerText"); h16 = J("location.hash"); t16 = toast()
        rod = J("[...document.querySelectorAll('aside[role=dialog] .pe-form button')].map(b=>b.innerText.trim())")
        J("[...document.querySelectorAll('aside[role=dialog] .pe-form button')].pop().click()"); time.sleep(.5); e16 = est()
        J("location.hash='#plano=MILHO-SF'"); espera("document.querySelector('main h2')&&document.querySelector('main h2').innerText==='Milho safrinha'", 4); mi = J("document.querySelector('main').innerText")
        chk('L16 R4: com o painel "Atividade · Dessecação pré-plantio" aberto, trocar o endereço para #plano=MILHO-SF não troca de plano: o endereço volta, o painel continua o mesmo ("Salvar"), com aviso; salvar fica na Soja; o Milho continua sem rascunho e sem "Dessecação pré-plantio"',
            p0 == 'Atividade · Dessecação pré-plantio' and p1 == p0 and h16 == '#plano=SOJA-AT' and 'Feche o painel antes de trocar de plano.' in t16 and rod == ['Cancelar', 'Salvar']
            and e16['h2'] == 'Soja alta tecnologia' and 'Publicado · v4' in mi and 'Rascunho v5' not in mi and 'Dessecação pré-plantio' not in mi, [p0, p1, h16, t16, rod, e16['h2'], mi[:300]])
    # ---------------- L17 · R6: Esc fecha só a camada de cima ----------------
    # 13/10/2026 (proprietário: "deixe a barra lateral dos menus somente recolhido com os ícones e tooltip sem opção de expandir"): a 390 px
    # não há mais menu sobreposto para o Esc fechar. A parte de 390 px passa a ser a do filtro de coluna (por toque) e a barra recolhida
    FILTRO = "[...document.querySelectorAll('main button')].find(b=>b.getClientRects().length&&/^Filtrar /.test(b.getAttribute('aria-label')||''))"
    FOCA = "(()=>{const d=[...document.querySelectorAll('div[role=dialog]')].find(x=>x.getClientRects().length); if(!d) return false; const b=[...d.querySelectorAll('button')].find(x=>x.getClientRects().length); b&&b.focus(); return document.activeElement===b;})()"
    ABERTO = "!![...document.querySelectorAll('div[role=dialog]')].find(x=>x.getClientRects().length)"
    BARRA = r"""(()=>{const m=document.querySelector('nav[aria-label=Menu]'); const vis=e=>!!e&&e.getClientRects().length>0;
      const exp=[...document.querySelectorAll('button,[role=button],a,label')].filter(vis).filter(e=>/\b(expandir|recolher|abrir|fechar)\b.{0,12}\bmenu\b/i.test((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')+' '+e.innerText)).length;
      return [Math.round(m.getBoundingClientRect().width), exp, getComputedStyle(m).position==='absolute'||vis(document.querySelector('.ml-fundo'))];})()"""
    with secao('L17'):
        abre('PA.dc.html#plano=SOJA-AT')
        clique(FILTRO, w=.5); f0 = J(FOCA)
        c.tecla('Escape', 'Escape', 27); time.sleep(.5); f1 = est(); fa = J(ABERTO)
        abre('PA.dc.html#plano=SOJA-AT', 390, 844, 3, True); b0 = J(BARRA)
        clique(FILTRO, True, .5); g0 = J(FOCA); shot('L17_390_filtro')
        c.tecla('Escape', 'Escape', 27); time.sleep(.5); g1 = est(); ga = J(ABERTO); b1 = J(BARRA)
        chk('L17 R6: Esc com o filtro de coluna dos cultivos aberto fecha só o filtro (o plano continua aberto), a 1440 px e a 390 px (toque); a 390 px a barra lateral fica recolhida (68 px), sem botão de expandir nem menu sobreposto',
            f0 and not fa and f1['h2'] == 'Soja alta tecnologia' and f1['hash'] == '#plano=SOJA-AT' and b0 == [68, 0, False]
            and g0 and not ga and g1['h2'] == 'Soja alta tecnologia' and g1['hash'] == '#plano=SOJA-AT' and b1 == [68, 0, False], [f0, fa, f1['h2'], f1['hash'], b0, g0, ga, g1['h2'], g1['hash'], b1])
    # ---------------- L18 · R7: aviso sem o id interno ----------------
    with secao('L18'):
        abre('PA.dc.html'); clique(btn('Criar plano'), w=.5)
        J("(()=>{const s=document.querySelector('#np_cult'); const P=HTMLSelectElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(s,'Soja'); s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
        J("(()=>{const i=document.querySelector('#np_nome'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'Soja teste'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
        clique(btn('Criar plano', "document.querySelector('aside[role=dialog]')"), w=.8); h18 = J("location.hash")
        recarrega(); espera("[...document.querySelectorAll('[role=status]')].some(x=>/não encontrado/.test(x.innerText))", 3); t18 = toast(); e18 = est()
        chk('L18 R7: plano novo e F5: abre a lista com o aviso "Plano do endereço não encontrado…", sem o id interno', h18.startswith('#plano=NP') and e18['cards'] == len(D2.PLANOS) and e18['hash'] == ''
            and 'Plano do endereço não encontrado' in t18 and h18.replace('#plano=', '') not in t18 and 'NP' not in t18, [h18, t18, e18['hash']])
    # ---------------- L19 · R8: sair com a inclusão de insumo digitada ----------------
    with secao('L19'):
        abre('PA.dc.html#plano=SOJA-AT'); clique(lab('Mostrar insumos de Fungicida 1ª aplicação'), w=.3); clique(lab('Incluir insumo em Fungicida 1ª aplicação'), w=.4)
        digita('Inset'); time.sleep(.4); c.tecla('ArrowDown', 'ArrowDown', 40); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.4); digita('0,3')
        clique("document.querySelector('[data-acoes] [data-acao=voltar]')", w=.5); w1 = est(); nt1 = J(NOTA)
        clique(btn('Continuar editando', "document.querySelector('[data-acoes]')"), w=.4); w2 = est(); dv = J("(()=>{const i=document.querySelector('[id^=pa-add-dose-]'); return i?{v:i.value, foco:document.activeElement===i}:null;})()")
        J("location.hash='#plano=MILHO-SF'"); espera("location.hash==='#plano=SOJA-AT'", 3); time.sleep(.3); w3 = est()
        clique(btn('Descartar e abrir Milho safrinha', "document.querySelector('[data-acoes]')"), w=.6); w4 = est()
        clique("document.querySelector('[data-acoes] [data-acao=voltar]')", w=.6); clique(CARD('Soja alta tecnologia'), w=.6); w5 = est(); ab = J("!!document.querySelector('[id^=pa-add-dose-]')")
        chk('L19 R8: "‹ Biblioteca de planos" com a inclusão de insumo digitada não sai e avisa ao lado ("Descartar e voltar à biblioteca" · "Continuar editando"); continuar mantém o que foi digitado; trocar o endereço avisa e o endereço volta; "Descartar e abrir Milho safrinha" abre o Milho; a Soja reabre sem a inclusão e sem rascunho',
            w1['h2'] == 'Soja alta tecnologia' and w1['hash'] == '#plano=SOJA-AT' and nt1['txt'].startswith('A inclusão de insumo não foi concluída: o que foi digitado se perde ao sair.')
            and 'atalho:Descartar e voltar à biblioteca' in w1['area'] and 'atalho:Continuar editando' in w1['area']
            and not any(a.startswith('atalho:Descartar') for a in w2['area']) and dv and dv['v'] == '0,3' and dv['foco']
            and w3['h2'] == 'Soja alta tecnologia' and w3['hash'] == '#plano=SOJA-AT' and 'atalho:Descartar e abrir Milho safrinha' in w3['area']
            and w4['h2'] == 'Milho safrinha' and w4['hash'] == '#plano=MILHO-SF' and w5['h2'] == 'Soja alta tecnologia' and not ab and not w5['prims'], [w1, nt1, w2['area'], dv, w3, w4['h2'], w5, ab])
    ERRL.extend(errs()); chk('L13 sem erro de JavaScript', not ERRL, ERRL[:5])
finally:
    if c: c.close()
    srv.terminate()
    if srv0: srv0.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas', flush=True)
sys.exit(1 if FAIL else 0)
