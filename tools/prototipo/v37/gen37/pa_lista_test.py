# -*- coding: utf-8 -*-
"""NAV-1 · Planos agronômicos sem etapas falsas (lista → detalhe) e o link do cultivo para o Planejar safra (X-AGR-6).
Aceite do docs/navegacao/CONSOLIDADO.md §3.1 e do design system de 09/10 (BOT-01..06, SEL-02, VIS-04), no Chrome headless:
  L1  sem faixa de etapas (.etp-ind) e sem "impedida", na lista e no detalhe
  L2  lista: um cartão por plano; o único verde é "Criar plano", no cabeçalho, à direita do título (BOT-01/02/03/05)
  L3  cartão → detalhe com #plano=SOJA-AT; sem rascunho, nenhuma primária; "‹ Biblioteca de planos" no Próximo passo; Atividades,
      Cultivos e Versões visíveis; "Incluir atividade" branco e compacto no cabeçalho do bloco Atividades, com "+"
  L4  F5 reabre o mesmo plano; #plano=XYZ abre a lista, sem erro; trocar o endereço para #plano=MILHO-SF abre o Milho
  L5  mudar uma dose na tabela: UMA primária "Salvar alterações"; o resumo das alterações na nota, ao lado dela e NA TELA
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
  L12 cliques para "mudar uma dose e publicar" (abrir o plano, abrir a atividade, tocar a dose, digitar 0,45 + Enter, publicar):
      medidos na execução real; com ANTES=<_render da base> mede também a base cdc185f no mesmo cenário (1 a menos)
  Revisão adversarial do Codex (09/10), um caso por achado, com a reprodução dele:
  L14 R1/R2 (leve, proprietário 19/10: "leve e fluido"; antes o clique só gravava a dose e pedia um 2º clique): dose digitada sem
      Enter e um clique de verdade em "Salvar e publicar" publicam a v7 com essa dose, e o aviso diz qual dose entrou; a dose 0 sem
      Enter não publica e o erro continua no campo
  L15 R3: rascunho que volta a ficar igual à v6 desabilita "Publicar" com o motivo
  L16 R4: trocar o endereço com o painel da atividade aberto não troca de plano (endereço volta) nem grava em outro plano
  L17 R6: Esc com o menu ⋯ da atividade aberto fecha só o menu, a 1440 e a 390 px (toque); a 390 px a barra lateral fica recolhida
      (68 px, sem expandir: proprietário, 13/10/2026; antes: Esc com o menu sobreposto fechava só o menu)
  L18 R7: plano novo e F5: reabre o rascunho v1 guardado (PA-OPER F1, decisão 9) e o aviso não mostra o id interno
  L19 R8: voltar ou trocar de plano com a inclusão de insumo digitada avisa ("Descartar e …" ou "Continuar editando")
  L13 sem erro de JavaScript
Uso (de gen37/): python3 pa_lista_test.py           (RENDER_DIR=<outro _render> roda contra outro build; sai 1 se falhar)
                 ANTES=<_render da base> python3 pa_lista_test.py   (inclui a medida da base em L12)
PA-OPER F1 (19/10): dose de exemplo 0,6 → 0,45 L/ha (0,6 passa da bula de demonstração e impede publicar: P7); Glifosato 6 → 2,5 L/ha (máximo
3 L/ha na bula); primária "Salvar e publicar vN"; selo "Publicada vN"; o plano novo fica guardado no cenário (L18).
Emulação no Chrome headless; não é aparelho físico."""
import sys, os, time, json, re
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
 return {prims, area, rot:a?a.getAttribute('aria-label'):'', faixa:!!document.querySelector('.etp-ind,.etp'), impedida:/impedid/i.test(document.body.innerText.replace(/\d+ operaç(ão|ões) impedidas?|⛔ Impedida/g,'')), tit, hash:location.hash,
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
    if abrir and J(f"!!{lab('Abrir insumos de Fungicida 1ª aplicação')}"): clique(lab('Abrir insumos de Fungicida 1ª aplicação'), toque)
    clique(lab('Alterar a dose de Fungicida A'), toque, .3)
    J("document.activeElement&&document.activeElement.select&&document.activeElement.select()"); digita(val); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.45)
def publicar_ate(toque=False):
    """anda pelo caminho que a tela oferece até 'Salvar alterações' (na base passa por 'Revisar e publicar ›') e publica"""
    for _ in range(3):
        if J(f"!!{btnc('Salvar e publicar')}"): break
        if clique("document.querySelector('[data-acoes] [data-acao=avancar]')", toque, .6) != 'ok': break
    return clique(btnc('Salvar e publicar'), toque, .6)
def cenario_cliques(porta, toque=False, w=1440, h=900):
    """mudar uma dose (Fungicida A 0,5 → 0,45 L/ha) e publicar a v7, do índice do menu (lista) até a versão publicada"""
    abre('PA.dc.html', w, h, 3 if toque else 1, toque, porta=porta); CLIQUES[0] = 0
    clique(CARD('Soja alta tecnologia'), toque, .7); mudar_dose('0,45', toque); r = publicar_ate(toque)
    return CLIQUES[0], 4 + 1, r, toast()   # teclas: "0,45" (4) + Enter
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
        chk('L3 cartão → detalhe #plano=SOJA-AT; sem rascunho nenhuma primária; Próximo passo só com "‹ Biblioteca de planos"; só o bloco Atividades (Cultivos e Versões saíram em 14/10); "Incluir atividade" branco, compacto, com "+", no cabeçalho do bloco Atividades',
            d['hash'] == '#plano=SOJA-AT' and d['h2'] == 'Soja alta tecnologia' and d['prims'] == [] and d['area'] == ['voltar:‹ Biblioteca de planos'] and d['rot'] == 'Próximo passo'
            and 'Atividades do plano' in d['tit'] and not any('Cultivos que usam' in t for t in d['tit']) and not any(t.endswith('Versões') for t in d['tit'])
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
        abre('PA.dc.html#plano=SOJA-AT'); mudar_dose('0,45'); t1 = toast(); m = est(); shot('1440_rascunho')
        ordem = J(r"""(()=>{const a=document.querySelector('[data-acoes]'); const ss=[...document.querySelectorAll('main section')].filter(s=>s.getClientRects().length); const u=ss[ss.length-1]; if(!a||!u) return {ultimo:'',depois:false,texto:''};
          return {ultimo:(u.querySelector('h3')||{innerText:''}).innerText.trim(), depois:!!(u.compareDocumentPosition(a)&Node.DOCUMENT_POSITION_FOLLOWING), texto:u.innerText.replace(/\s+/g,' ')};})()""")
        nt = J(NOTA); alt = J("!!document.getElementById('pa-alt-tit')")
        sel = J("[...document.querySelectorAll('main .pa-atividade')].filter(a=>/Alterada/.test(a.innerText)).map(a=>(a.querySelector('.pa-titulo')||{innerText:''}).innerText.trim())") or []
        # 14/10/2026 (proprietário: "tire essa parte de alterações de rascunho. lá embaixo deixe o botão salvar"): sem bloco e sem nota; a
        # atividade mudada fica marcada na lista e o aviso ao salvar diz o que mudou (L6)
        chk('L5 mudar a dose na tabela: rascunho v7; UMA primária "Salvar alterações", sem nota ao lado e sem o bloco de alterações; a atividade mudada fica marcada "Alterada"',
            'Rascunho v7 criado' in t1 and [x['t'] for x in m['prims']] == ['Salvar e publicar v7'] and not m['prims'][0]['dis'] and 'comando:Salvar e publicar v7' in m['area']
            and not nt['txt'] and not alt and 'Fungicida 1ª aplicação' in sel, [t1, m, nt, alt, sel, ordem])
        mudar_dose('0,4', abrir=False); t2 = toast(); m2 = est()
        clique(btn('Salvar e publicar v7'), w=.7); t3 = toast(); m3 = est(); shot('1440_publicado'); foco = J("(document.activeElement&&document.activeElement.id)||''")
        corpo = J("document.querySelector('main').innerText")
        chk('L6 repetição: a 2ª mudança fica no rascunho v7 (uma primária); salvar: aviso curto "Plano salvo · v7 · cultivos seguem na versão deles" (15/10, proprietário: pouco texto); "Publicado · v7", sem primária nem bloco de alterações; o foco vai ao nome do plano',
            'Gravado no rascunho v7' in t2 and [x['t'] for x in m2['prims']] == ['Salvar e publicar v7'] and t3.startswith('Publicada v7') and 'cultivos seguem na versão deles' in t3 and m3['prims'] == [] and m3['area'] == ['voltar:‹ Biblioteca de planos']
            and not any(t.startswith('Alterações do rascunho') for t in m3['tit']) and 'Publicada v7' in corpo and foco == 'pa-det-tit' and len(t3) <= 60 and 'decida a adoção' not in t3 + corpo,
            [t2, m2['prims'], t3, m3, foco])
    # ---------------- L8 · link ao Planejar safra ----------------
    with secao('L8'):
        # o link "Abrir cultivo no Planejar safra ›" saiu com o bloco Cultivos (14/10); o endereço direto do cultivo continua valendo
        c.goto(f'http://127.0.0.1:{p}/SAF.dc.html#saf=S2627&passo=cultivos&cult=c1', .2)
        espera("location.pathname.endsWith('SAF.dc.html')&&!![...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length&&/T1-A/.test(x.innerText))", 8)
        sf = J("(()=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const cur=document.querySelector('.etp-ind [aria-current=step]'); const d=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); return {url:location.pathname.split('/').pop()+location.hash, etapa:cur?n(cur.innerText):'', painel:d?n(d.innerText).slice(0,160):''};})()"); shot('1440_saf_cultivo')
        chk('L8 o endereço do cultivo abre o Planejar safra na etapa 2 (Cultivos) da 2026/27 com o painel do cultivo c1 (T1-A)',
            sf['url'] == 'SAF.dc.html#saf=S2627&passo=cultivos&cult=c1' and sf['etapa'].startswith('2') and 'T1-A' in sf['painel'], sf)
    # ---------------- L7 · erro e recusa ----------------
    with secao('L7'):
        abre('PA.dc.html#plano=SOJA-AT')
        clique(lab('Abrir insumos de Fungicida 1ª aplicação')); clique(lab('Alterar a dose de Fungicida A'), w=.3)
        J("document.activeElement.select()"); digita('0'); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.4)
        e0 = J("[...document.querySelectorAll('main [role=alert]')].map(a=>a.innerText.trim()).join(' | ')"); r0 = est()
        c.tecla('Escape', 'Escape', 27); time.sleep(.3); r0b = est()
        clique(lab('Incluir insumo em Fungicida 1ª aplicação'), w=.4); mudar_dose('0,45', abrir=False)   # inclusão aberta + rascunho
        espera(f"!!{PUB}&&!{PUB}.disabled")
        clique(lab('Incluir insumo em Fungicida 1ª aplicação'), w=.1); espera(f"!!{PUB}&&{PUB}.disabled&&!!document.querySelector('[id^=pa-add-dose-]')")
        ia = est(); nota = J("(document.querySelector('[data-acoes] .acoes-nota')||{innerText:''}).innerText.trim()")
        clique(btn('Cancelar', "document.querySelector('main')"), w=.1); espera(f"!document.querySelector('[id^=pa-add-dose-]')&&!!{PUB}&&!{PUB}.disabled"); ib = est()
        chk('L7a dose 0 recusada junto ao campo sem criar rascunho; Esc cancela e o detalhe continua sem primária; com a inclusão de insumo aberta, "Incluir" verde na linha e "Salvar alterações" desabilitado com o motivo (nota e dica); Cancelar devolve',
            'Informe a dose por hectare, maior que zero.' in e0 and r0['prims'] == [] and r0b['prims'] == [] and r0b['h2'] == 'Soja alta tecnologia'
            and [p['t'] for p in ia['prims']] == ['Incluir', 'Salvar e publicar v7'] and not ia['prims'][0]['dis']   # 15/10 (proprietário): "Incluir" é a primária verde da linha de inclusão
            and ia['prims'][1]['dis'] and ia['prims'][1]['why'] == 'Conclua ou cancele a inclusão do insumo para salvar.' and nota == ia['prims'][1]['why']
            and len(ib['prims']) == 1 and not ib['prims'][0]['dis'], [e0, r0, r0b, ia, nota, ib])
        clique("document.querySelector('[data-acoes] [data-acao=voltar]')", w=.6)
        clique(btn('Criar plano'), w=.5)
        J("(()=>{const s=document.querySelector('#np_cult'); const P=HTMLSelectElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(s,'Soja'); s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
        J("(()=>{const i=document.querySelector('#np_nome'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'soja ALTA tecnologia'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
        rodape = J("[...document.querySelectorAll('aside[role=dialog] .pe-form button')].map(b=>b.innerText.trim())")
        clique(btn('Criar plano', "document.querySelector('aside[role=dialog]')"), w=.4); dup = J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText")
        J("(()=>{const i=document.querySelector('#np_nome'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'Soja teste'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
        clique(btn('Criar plano', "document.querySelector('aside[role=dialog]')"), w=.8); nv = est(); nota2 = J("(document.querySelector('[data-acoes] .acoes-nota')||{innerText:''}).innerText.trim()")
        chk('L7b plano novo: rodapé "Cancelar · Criar plano"; nome repetido na cultura recusado; em branco abre o detalhe #plano= com "Salvar alterações" desabilitado e o motivo; o bloco Atividades mantém "Incluir atividade"',
            rodape == ['Cancelar', 'Criar plano'] and 'Já existe um plano com este nome nesta cultura.' in dup and nv['h2'] == 'Soja teste' and nv['hash'].startswith('#plano=NP')
            and len(nv['prims']) == 1 and nv['prims'][0]['t'] == 'Salvar e publicar v1' and nv['prims'][0]['dis'] and nota2 == 'Inclua ao menos uma atividade para salvar.'
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
        ROL = "[...document.querySelectorAll('main[data-scroll],.ml-tog+div')].map(e=>Math.round(e.scrollTop))"
        # 14/10 (cartão sem o rodapé dos cultivos): a biblioteca ficou mais curta; a prova é voltar à mesma rolagem de antes de abrir, não um valor fixo
        centro("[...document.querySelectorAll('main .g2card')].pop()"); time.sleep(.3); antes = J(ROL)   # a mesma rolagem do clique (o clique centraliza o cartão)
        clique("[...document.querySelectorAll('main .g2card')].pop()", w=.7)
        clique("document.querySelector('[data-acoes] [data-acao=voltar]')", w=.7); dep = J(ROL); fcs = J("(document.activeElement&&document.activeElement.getAttribute('aria-label'))||''")
        cur = J("(document.querySelector('main .g2card[aria-current=true]')||{getAttribute:()=>''}).getAttribute('aria-label')")
        chk('L10 "‹ Biblioteca de planos" volta à posição de rolagem da biblioteca, com o foco e a marca no último cartão aberto', max(antes) > 0 and dep == antes and fcs == ult and cur == ult, [antes, dep, fcs, ult, cur])
    # ---------------- L11 · 390 px (toque) ----------------
    with secao('L11'):
        abre('PA.dc.html', 390, 844, 3, True); a = J(r"""(()=>{const b=[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Criar plano'); const r=b?b.getBoundingClientRect():null;
          return {lado:document.documentElement.scrollWidth>innerWidth+1, criar:!!r&&r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight};})()"""); shot('390_lista')
        clique(CARD('Soja alta tecnologia'), True, .8); mudar_dose('0,45', True); n390 = J(NOTA)
        b = J(r"""(()=>{const e=document.querySelector('[data-acoes] [data-acao=comando]'); const r=e?e.getBoundingClientRect():null; const t=r?document.elementFromPoint(r.left+r.width/2,r.top+r.height/2):null;
          return {lado:document.documentElement.scrollWidth>innerWidth+1, prim:e?e.innerText.trim():'', naTela:!!r&&r.top>=0&&r.bottom<=innerHeight&&r.left>=0&&r.right<=innerWidth&&!!t&&e.contains(t)};})()"""); shot('390_rascunho')
        clique("document.querySelector('[data-acoes] [data-acao=comando]')", True, .7); t390 = toast()
        chk('L11 390 px (toque): sem rolagem lateral; "Criar plano" na tela; depois de mudar a dose, "Salvar alterações" na tela, sem nada por cima e sem nota; salvar pelo toque e o aviso curto diz a versão salva',
            not a['lado'] and a['criar'] and not b['lado'] and b['prim'] == 'Salvar e publicar v7' and b['naTela'] and not n390['txt']
            and t390.startswith('Publicada v7'), [a, b, n390, t390])
    # ---------------- L12 · cliques medidos (mesmo cenário) ----------------
    with secao('L12'):
        n1, tec1, r1, tt1 = cenario_cliques(p)
        res = {'depois': (n1, tec1, 'Publicada v7' in tt1)}
        if ANTES:
            n0, tec0, r0_, tt0 = cenario_cliques(p0); res['antes cdc185f'] = (n0, tec0, 'Versão v7 publicada' in tt0)
        info('cliques e teclas para mudar uma dose e publicar (cliques, teclas, publicou)', res)
        chk('L12 mudar uma dose e publicar: 4 cliques (abrir o plano, abrir a atividade, tocar a dose, publicar) + "0,45" e Enter; com ANTES, 1 a menos que a base no mesmo cenário',
            res['depois'] == (4, 5, True) and (not ANTES or (res['antes cdc185f'][2] and res['antes cdc185f'][0] - n1 == 1)), res)
    # ---------------- L14 · R1/R2: dose sem Enter e "Publicar" ----------------
    with secao('L14'):
        abre('PA.dc.html#plano=SOJA-AT'); mudar_dose('0,45')
        clique(lab('Abrir insumos de Dessecação pré-plantio'), w=.3); clique(lab('Alterar a dose de Glifosato 480'), w=.3)
        J("document.activeElement.select&&document.activeElement.select()"); digita('2,5'); aberta = J(NOTA)
        clique(PUB, w=.1); espera("[...document.querySelectorAll('[role=status]')].some(x=>/Publicada v7/.test(x.innerText))", 4)
        t14 = toast(); v14 = J("document.querySelector('main').innerText.replace(/\\s+/g,' ')")   # Versões saiu do detalhe (14/10): o cabeçalho diz a versão em vigor
        chk('L14a R1 (leve): dose do Glifosato 480 digitada (2,5) sem Enter: "Salvar e publicar v7" habilitado, sem nota; um clique de verdade publica a v7 e o aviso diz "inclui Glifosato 480: 2 → 2,5 L/ha"',
            not aberta['dis'] and not aberta['txt'] and 'Publicada v7' in t14 and 'inclui Glifosato 480: 2 → 2,5 L/ha' in t14
            and 'Publicada v7' in v14 and 'Rascunho v7' not in v14, [aberta, t14, v14[:400]])
        clique(lab('Abrir insumos de Dessecação pré-plantio'), w=.3) if J(f"!!{lab('Abrir insumos de Dessecação pré-plantio')}") else None
        g14 = J(f"(()=>{{const b={lab('Alterar a dose de Glifosato 480')}; return b?b.innerText.trim():'';}})()")
        clique(lab('Abrir insumos de Fungicida 1ª aplicação'), w=.3) if J(f"!!{lab('Abrir insumos de Fungicida 1ª aplicação')}") else None
        f14 = J(f"(()=>{{const b={lab('Alterar a dose de Fungicida A')}; return b?b.innerText.trim():'';}})()")
        chk('L14b R1 (leve): a v7 publicada leva as duas doses (Glifosato 480 em 2,5 L/ha e Fungicida A em 0,45 L/ha), sem 2º clique', g14 == '2,5 L/ha' and f14 == '0,45 L/ha', [g14, f14])
        abre('PA.dc.html#plano=SOJA-AT'); mudar_dose('0,45'); clique(lab('Alterar a dose de Fungicida A'), w=.3)
        J("document.activeElement.select&&document.activeElement.select()"); digita('0'); clique(PUB, w=.6)
        t2 = toast(); a2 = J("[...document.querySelectorAll('main [role=alert]')].map(a=>a.innerText.trim()).join(' | ')"); n2 = J(NOTA); campo = J("(document.querySelector('input[id^=pa-dose-]')||{value:null}).value")
        chk('L14c R2: dose 0 digitada sem Enter e clique em "Salvar e publicar": não publica; o erro continua junto ao campo aberto, com o 0',
            'Publicada' not in t2 and 'Informe a dose por hectare, maior que zero.' in a2 and campo == '0' and 'Publicada' not in J("document.querySelector('main').innerText"), [t2, a2, n2, campo])
    # ---------------- L15 · R3: rascunho igual à versão publicada ----------------
    with secao('L15'):
        abre('PA.dc.html#plano=SOJA-AT'); mudar_dose('0,45'); mudar_dose('0,5', abrir=False); n15 = J(NOTA); e15 = est()
        chk('L15 R3: 0,5 → 0,45 → 0,5 deixa o rascunho v7 igual à v6: "Salvar alterações" desabilitado com o motivo (sem v7 vazia, sem cultivo marcado)',
            len(e15['prims']) == 1 and e15['prims'][0]['dis'] and n15['txt'] == 'O rascunho v7 está igual à v6: altere algo ou descarte o rascunho.' and e15['prims'][0]['why'] == n15['txt'], [n15, e15])
    # ---------------- L16 · R4: endereço trocado com o painel aberto ----------------
    with secao('L16'):
        abre('PA.dc.html#plano=SOJA-AT'); clique("[...document.querySelectorAll('main .pa-mais')].find(b=>b.getClientRects().length)", w=.3)   # VISOES-2: editar está no menu ⋯
        clique("[...document.querySelectorAll('main [role=menu] button')].find(b=>b.innerText.trim()==='Editar atividade')", w=.5)
        p0 = J("(document.querySelector('aside[role=dialog] h2')||{innerText:''}).innerText")
        J("location.hash='#plano=MILHO-SF'"); espera("location.hash==='#plano=SOJA-AT'", 3); time.sleep(.3)
        p1 = J("(document.querySelector('aside[role=dialog] h2')||{innerText:''}).innerText"); h16 = J("location.hash"); t16 = toast()
        rod = J("[...document.querySelectorAll('aside[role=dialog] .pe-form button')].map(b=>b.innerText.trim())")
        J("[...document.querySelectorAll('aside[role=dialog] .pe-form button')].pop().click()"); time.sleep(.5); e16 = est()
        J("location.hash='#plano=MILHO-SF'"); espera("document.querySelector('main h2')&&document.querySelector('main h2').innerText==='Milho safrinha'", 4); mi = J("document.querySelector('main').innerText")
        chk('L16 R4: com o painel "Atividade · Dessecação pré-plantio" aberto, trocar o endereço para #plano=MILHO-SF não troca de plano: o endereço volta, o painel continua o mesmo ("Salvar"), com aviso; salvar fica na Soja; o Milho continua sem rascunho e sem "Dessecação pré-plantio"',
            p0 == 'Atividade · Dessecação pré-plantio' and p1 == p0 and h16 == '#plano=SOJA-AT' and 'Feche o painel antes de trocar de plano.' in t16 and rod == ['Cancelar', 'Salvar']
            and e16['h2'] == 'Soja alta tecnologia' and 'Publicada v4' in mi and 'Rascunho v5' not in mi and 'Dessecação pré-plantio' not in mi, [p0, p1, h16, t16, rod, e16['h2'], mi[:300]])
    # ---------------- L17 · R6: Esc fecha só a camada de cima ----------------
    # 13/10/2026 (proprietário: "deixe a barra lateral dos menus somente recolhido com os ícones e tooltip sem opção de expandir"): a 390 px
    # não há mais menu sobreposto para o Esc fechar. A parte de 390 px passa a ser a do filtro de coluna (por toque) e a barra recolhida
    # 14/10/2026: o filtro de coluna saiu com o bloco Cultivos; a camada de cima do detalhe passa a ser o menu ⋯ da atividade
    FILTRO = "[...document.querySelectorAll('main .pa-mais')].find(b=>b.getClientRects().length)"
    FOCA = "(()=>{const m=[...document.querySelectorAll('main [role=menu]')].find(x=>x.getClientRects().length); return !!m&&m.contains(document.activeElement);})()"
    ABERTO = "!![...document.querySelectorAll('main [role=menu]')].find(x=>x.getClientRects().length)"
    VOLTA = "!!(document.activeElement&&document.activeElement.classList.contains('pa-mais'))"
    BARRA = r"""(()=>{const m=document.querySelector('nav[aria-label=Menu]'); const vis=e=>!!e&&e.getClientRects().length>0;
      const exp=[...document.querySelectorAll('button,[role=button],a,label')].filter(vis).filter(e=>/\b(expandir|recolher|abrir|fechar)\b.{0,12}\bmenu\b/i.test((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')+' '+e.innerText)).length;
      return [Math.round(m.getBoundingClientRect().width), exp, getComputedStyle(m).position==='absolute'||vis(document.querySelector('.ml-fundo'))];})()"""
    with secao('L17'):
        abre('PA.dc.html#plano=SOJA-AT')
        clique(FILTRO, w=.5); f0 = J(FOCA)
        c.tecla('Escape', 'Escape', 27); time.sleep(.5); f1 = est(); fa = J(ABERTO); fv = J(VOLTA)
        abre('PA.dc.html#plano=SOJA-AT', 390, 844, 3, True); b0 = J(BARRA)
        clique(FILTRO, True, .5); g0 = J(FOCA); shot('L17_390_filtro')
        c.tecla('Escape', 'Escape', 27); time.sleep(.5); g1 = est(); ga = J(ABERTO); b1 = J(BARRA); gv = J(VOLTA)
        chk('L17 R6: Esc com o menu ⋯ da atividade aberto (foco no 1º item) fecha só o menu e devolve o foco ao ⋯ (o plano continua aberto), a 1440 px e a 390 px (toque); a 390 px a barra lateral fica recolhida (68 px), sem botão de expandir nem menu sobreposto',
            f0 and not fa and fv and gv and f1['h2'] == 'Soja alta tecnologia' and f1['hash'] == '#plano=SOJA-AT' and b0 == [68, 0, False]
            and g0 and not ga and g1['h2'] == 'Soja alta tecnologia' and g1['hash'] == '#plano=SOJA-AT' and b1 == [68, 0, False], [f0, fa, fv, f1['h2'], f1['hash'], b0, g0, ga, gv, g1['h2'], g1['hash'], b1])
    # ---------------- L18 · R7: aviso sem o id interno ----------------
    with secao('L18'):
        abre('PA.dc.html'); clique(btn('Criar plano'), w=.5)
        J("(()=>{const s=document.querySelector('#np_cult'); const P=HTMLSelectElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(s,'Soja'); s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
        J("(()=>{const i=document.querySelector('#np_nome'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'Soja teste'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
        clique(btn('Criar plano', "document.querySelector('aside[role=dialog]')"), w=.8); h18 = J("location.hash")
        recarrega(); espera("document.querySelector('main h2')&&/Soja teste/.test(document.querySelector('main h2').innerText)", 4); t18 = toast(); e18 = est()
        # PA-OPER F1 (decisão 9, P17): o rascunho fica guardado no cenário; o plano novo reabre no F5 como rascunho v1, sem id interno no aviso
        chk('L18 R7: plano novo e F5: reabre o próprio plano como rascunho v1 (guardado no cenário), sem o id interno no aviso', h18.startswith('#plano=NP') and e18['h2'] == 'Soja teste'
            and e18['hash'].startswith('#plano=NP') and h18.replace('#plano=', '') not in t18 and 'NP' not in t18 and 'Rascunho v1' in J("document.body.innerText"), [h18, t18, e18['hash'], e18['h2']])
    # ---------------- L19 · R8: sair com a inclusão de insumo digitada ----------------
    with secao('L19'):
        abre('PA.dc.html#plano=SOJA-AT'); clique(lab('Abrir insumos de Fungicida 1ª aplicação'), w=.3); clique(lab('Incluir insumo em Fungicida 1ª aplicação'), w=.4)
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
