# -*- coding: utf-8 -*-
"""F3 da base verde (19/10/2026): o "×" de fechar dos painéis tem alvo de toque de 44 px com ponteiro grosso (DS-ALVO-20261015),
pela regra comum do ALVO_CSS (engine), sem mudar o desktop. Painéis abertos pela tela, como o usuário faria.
  A0 inventário do render: todo "×" de fechar com largura menor que 44 px no estilo é quadrado e tem o tamanho em ALVO_FECHAR (a regra o cobre)
  A1 390 × 844 com toque: em cada painel aberto (CF-06 Metas, CF-01 Usuários, O.S., ordens da Manutenção e os dois painéis do Mapa, de
     30 px: o do talhão e o da importação de talhões) o "×" é medido e mede ≥ 44 × 44 px; tela sem medida reprova
  A2 1440 × 900 com mouse: o mesmo "×" continua no tamanho do estilo (32 ou 30 px; o desktop não muda), também em todas as telas
  A3 o fundo escuro, que também fecha o painel, não ganha tamanho (continua cobrindo a tela, sem largura fixa)
  A4 nenhum erro de JavaScript
  A5 390 px com toque, nos dois painéis do Mapa: o "×" de 44 px fica inteiro na tela (rolada até o painel, que a 390 px fica abaixo do mapa)
     e não se sobrepõe a outro elemento do cabeçalho do painel
Achados do app no PR #135: 4311810128 (os 30 px do Mapa ficavam fora) e 4311851179 (a Manutenção não era medida e o teste aceitava 3 de 4).
Contraprova: o render da composição 5bc0b340 reprova A1; o engine.py do HEAD 43a83f73 (só 32 px) reprova A0 e A1 no Mapa.
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B alvo_fechar_test.py"""
import os, sys, json, time, re, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:900])
# painel e o que o abre: a primeira linha da tabela da tela; no Mapa, o primeiro talhão (foco + Enter, como no teclado)
TELAS = [('CF-06', 'CF-06.dc.html', '[data-g2g=g_metas] [role=row][data-rid]'), ('CF-01', 'CF-01.dc.html', '[role=row][data-rid]'),
         ('O.S.', 'OS.dc.html', '[role=row][data-rid]'), ('Manutenção', 'MA.dc.html#vis=ordens', '[data-g2g=g_om] [role=row][data-rid]'),
         ('Mapa · talhão', 'IN-04.dc.html', '[data-mux-grupo] [data-talhao]'), ('Mapa · importar', 'IN-04.dc.html', 'IMPORTAR')]
# A5: o "×" pequeno inteiro na tela e sem sobrepor os vizinhos no cabeçalho do painel
CAB = """JSON.stringify([...document.querySelectorAll("button[aria-label^='Fechar']")].filter(b=>b.getClientRects().length&&/(?:^|[^-])width: [0-9]+px/.test(b.getAttribute('style')||'')).map(b=>{
  b.scrollIntoView({block:'center'});   // a 390 px o painel do Mapa fica abaixo do mapa: a pessoa rola até ele
  const r=b.getBoundingClientRect(), dentro=r.left>=0&&r.top>=0&&r.right<=innerWidth&&r.bottom<=innerHeight;
  const viz=[...b.parentElement.children].filter(x=>x!==b&&x.getClientRects().length).map(x=>x.getBoundingClientRect()).filter(q=>q.left<r.right-1&&q.right>r.left+1&&q.top<r.bottom-1&&q.bottom>r.top+1).length;
  return [dentro, viz]; }))"""
# o "×" desenhado à mão: largura menor que 44 px no estilo; devolve [largura medida, altura medida, largura do estilo]
XIS = """JSON.stringify([...document.querySelectorAll("button[aria-label^='Fechar']")].filter(b=>b.getClientRects().length).map(b=>{ const m=/(?:^|[^-])width: (\\d+)px/.exec(b.getAttribute('style')||'');
  return m&&Number(m[1])<44?(r=>[Math.round(r.width),Math.round(r.height),Number(m[1])])(b.getBoundingClientRect()):null; }).filter(Boolean))"""
FUNDO = """JSON.stringify([...document.querySelectorAll("button[aria-label^='Fechar'][tabindex='-1']")].filter(b=>b.getClientRects().length).map(b=>{ const r=b.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height),innerWidth]; }))"""
p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
erros = []
def abre(pg, sel):
    c.goto('about:blank', .1); c.goto(U(pg), 1.8)
    if not J(f"!!document.querySelector({json.dumps(sel)})"):   # tabela recolhida (DRILL-RECOLHIDO): expande como o usuário
        J("(()=>{ const b=[...document.querySelectorAll('button')].find(b=>/Expandir tudo/.test(b.innerText)); if(b) b.click(); })()"); time.sleep(.6)
    if sel == 'IMPORTAR':   # painel da importação de talhões: o botão "Importar" da barra de ferramentas do Mapa
        for _ in range(60):
            if J("!!(window.__LGI&&window.__LGI.pronto)"): break
            time.sleep(.25)
        J("(()=>{ const b=document.querySelector('button[title^=\"Importar talhões\"]'); if(b) b.click(); })()")
    elif 'data-talhao' in sel:
        for _ in range(40):   # o Mapa desenha os talhões depois de carregar
            if J(f"!!document.querySelector({json.dumps(sel)})"): break
            time.sleep(.25)
        J(f"(()=>{{ const b=document.querySelector({json.dumps(sel)}); if(b) b.focus(); }})()"); time.sleep(.15); c.tecla('Enter', 'Enter', 13, '\r')
    else:
        J(f"(()=>{{ const r=document.querySelector({json.dumps(sel)}); if(r) (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); }})()")
    time.sleep(.8); erros.extend(J("window.__e") or [])
# A0 · inventário estático do render: todo "×" de fechar desenhado à mão com menos de 44 px está coberto pela regra comum
fora = {}
for f in sorted(glob.glob(os.path.join(R, '*.html'))):
    pag = open(f, encoding='utf-8', errors='ignore').read()
    cob = set(re.findall(r"button\[aria-label\^='Fechar'\]\[style\*='width: (\d+)px'\]", pag))   # tamanhos que a regra desta página cobre
    for m in re.finditer(r'<button[^>]*aria-label="Fechar[^"]*"[^>]*>', pag):
        w = re.search(r'(?:^|[^-])width:\s*(\d+)px', m.group(0)); h = re.search(r'(?:^|[^-])height:\s*(\d+)px', m.group(0))
        if w and int(w.group(1)) < 44 and (not h or h.group(1) != w.group(1) or w.group(1) not in cob):
            fora.setdefault(os.path.basename(f), []).append([w.group(1), h.group(1) if h else None])
chk('A0 inventário: todo "×" de fechar com menos de 44 px no estilo é quadrado e tem o tamanho coberto pela regra da própria página (ALVO_FECHAR)', not fora, fora)
try:
    med = {}
    for w, h, toque in ((390, 844, True), (1440, 900, False)):
        c.aparelho(w, h, 2 if toque else 1, toque); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
        for rot, pg, sel in TELAS:
            abre(pg, sel); med[(w, rot)] = (json.loads(J(XIS) or '[]'), json.loads(J(FUNDO) or '[]'), J("matchMedia('(pointer:coarse)').matches"), json.loads(J(CAB) or '[]'))
    print('      medidas:', {f'{k[0]} {k[1]}': v for k, v in med.items()})
    com = [(rot, med[(390, rot)][:3]) for rot, _, _ in TELAS]
    chk(f'A1 390 px com toque: em todas as {len(TELAS)} telas o "×" do painel aberto é medido e mede ≥ 44 × 44 px (inclusive o de 30 px do Mapa)',
        all(v[0] and v[2] and all(x[0] >= 44 and x[1] >= 44 for x in v[0]) for _, v in com) and any(x[2] == 30 for _, v in com for x in v[0]), com)
    des = [(rot, med[(1440, rot)][:3]) for rot, _, _ in TELAS]
    chk('A2 1440 px com mouse: em todas as telas o mesmo "×" continua no tamanho do estilo (32 ou 30 px)', all(v[0] and not v[2] and all(x[0] == x[2] and x[1] == x[2] for x in v[0]) for _, v in des), des)
    fundo = [x for k, v in med.items() for x in v[1]]
    chk('A3 o fundo escuro que fecha o painel continua cobrindo a tela (sem o alvo de 44 px)', bool(fundo) and all(x[0] >= x[2] - 1 for x in fundo), fundo)
    chk('A4 nenhum erro de JavaScript', not erros, erros[:5])
    mapa = [(rot, med[(390, rot)][3]) for rot, _, _ in TELAS if rot.startswith('Mapa')]
    chk('A5 390 px com toque, nos dois painéis do Mapa: o "×" fica inteiro na tela e não se sobrepõe a outro elemento do cabeçalho',
        len(mapa) == 2 and all(v and all(x[0] and x[1] == 0 for x in v) for _, v in mapa), mapa)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok')
sys.exit(1 if FAIL else 0)
