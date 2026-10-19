# -*- coding: utf-8 -*-
"""MAPA-FROTA F1 · máquinas das O.S. em execução no Mapa (docs/integracao/V71/MAPA-FROTA.md, aceites M1–M24), no render sintético.
  M1  universo: Santa Rita lista OS-0420 e OS-0421 (1 marcador: OS-0421); Lagoa Grande lista OS-0505, OS-0506 e OS-0507 (1 marcador: OS-0505);
      os IDs são os Em execução do cenário na fazenda e safra do mapa
  M2  1 clique liga e o seguinte desliga, nas nove funções; aria-pressed acompanha; função, filtros, seleção de talhão e zoom ficam iguais
  M3  tocar no marcador abre o painel com os campos da decisão 9; "Abrir O.S." leva a OS.dc.html#OS-0421
  M4  a posição simulada fica dentro do T2 (a âncora sintética converte de volta para o desenho) e a OS-0420, sem fonte, não tem marcador
  M5  relógio e corte de sinal de teste: 60 s "Atual"; 61 s "Sem sinal há 1 min", marcador vazado, sem seta e sem "parada"
  M7  pausa sem leitura (fixture): a O.S. continua na lista, sem marcador; impedida mostra o selo da O.S. e "estado desconhecido"
  M8  iniciar a OS-0424 (o PJ-3030 programado nela): as duas linhas dizem "Conflito · também na OS-…"
  M9  enviar a OS-0421 para conferência com o painel aberto: o marcador sai e o painel avisa "saiu de Em execução (agora Em conferência)"
  M10 Esc fecha o painel e devolve o foco ao marcador; a lista tem as colunas da decisão 10, em ordem estável por O.S.
  M12 "Ver no mapa" da O.S.: 1 clique abre o Mapa com o conjunto selecionado; com o contexto salvo na Lagoa Grande, faixa "Recorte temporário"
      e 'mapa-ctx' inalterado
  M13 Rui: só a lista, sem posição nem operador; a varredura do DOM, das dicas e dos aria-label não acha coordenada, nome do operador nem idade
  M14 30 s de leituras, ligar e desligar 10 vezes e recarregar: o cenário gravado fica igual byte a byte
  M15 mapa (aria-label), lista e painel com a mesma fonte e a mesma idade
  M16 1440 e 390 (toque): alternador, Lista e marcador com alvo ≥ 44 px; sem rolagem lateral; sem erro de JS
  M18 marcador com ícone, rótulo curto e selo com palavra; legenda com os ícones e os estados
  M19 "Posições simuladas · demonstração" na legenda; lista e painel dizem "simulação"; nenhum texto diz "telemetria"
  M20 com Máquinas ligada, cores e rótulos dos talhões e números da faixa iguais (nas nove funções)
  M24 fixture com leitura "Trabalhando" na OS-0420 (Impedida): aviso "Leitura contradiz o impedimento da O.S. · conferir"; selo intacto
Contraprova (M22): no render de antes da F1 (RENDER_DIR) não há alternador: M1–M3 e M12 reprovam.
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B mapa_frota_test.py"""
import os, sys, json, time, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:700])
# o cenário gravado é achado pelo conteúdo (ordens e pessoas), sem depender do nome da chave
ESTADO = "Object.keys(localStorage).find(k=>{ try{ const x=JSON.parse(localStorage.getItem(k)); return !!(x&&x.ordens&&x.ordens['OS-0421']); }catch(e){ return false; } })"
p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
erros = []
def espera(e, s=20):
    f = time.time() + s
    while time.time() < f:
        if J(e): return True
        time.sleep(.25)
    return False
def abre(faz='Santa Rita', perfil='Ana', w=1440, h=900, toque=False, hash_='', limpa=True, extra=''):
    c.aparelho(w, h, 1 if w > 400 else 2, toque); c.goto('about:blank', .1); c.goto(U('Main.dc.html'), .3)
    J(("localStorage.clear(); " if limpa else '') + "sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','%s'); sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'%s'})); %s 1" % (perfil, faz, extra))
    c.goto(U('IN-04.dc.html' + hash_), 1.2)
    if faz == 'Lagoa Grande': espera("!!(window.__LGI&&window.__LGI.pronto)", 30)
def liga():
    J("(()=>{const b=document.querySelector('[data-frota-tog]'); if(b&&b.getAttribute('aria-pressed')!=='true') b.click();})()"); time.sleep(1.0)
def lista():
    J("(()=>{const b=document.querySelector('[data-frota-lista]'); if(b&&b.getAttribute('aria-pressed')!=='true') b.click();})()"); time.sleep(.6)
    return json.loads(J("JSON.stringify([...document.querySelectorAll('[data-frota-painel] tr[data-frota-linha]')].map(tr=>[...tr.children].map(td=>td.innerText.trim())))") or '[]')
MK = "JSON.stringify([...document.querySelectorAll('[data-frota-os]')].filter(b=>b.getClientRects().length).map(b=>{const r=b.getBoundingClientRect(); return {os:b.getAttribute('data-frota-os'),al:b.getAttribute('aria-label'),txt:b.innerText,w:r.width,h:r.height,x:r.left+r.width/2,y:r.top+r.height/2,vaz:!!b.querySelector('.fr-vazado'),seta:!!b.querySelector('.fr-seta'),ic:!!b.querySelector('svg')};}))"
PAINEL = "(document.querySelector('[data-frota-painel]')||{}).innerText||''"
def foto_estado():   # todo o armazenamento local (cenário, preferências) mais o cenário em memória da página
    return J("JSON.stringify([Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]), window.__frotaTeste.cenario()])")
class Pare(Exception): pass
def m12():   # "Ver no mapa" na OS-0421 com o contexto salvo na Lagoa Grande
    c.aparelho(1440, 900); c.goto('about:blank', .1); c.goto(U('Main.dc.html'), .3)
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana'); sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:'Lagoa Grande'})); 1")
    c.goto(U('OS.dc.html#OS-0421'), 1.5)
    lk = J("(()=>{ const a=document.querySelector('a[data-frota-link]'); return a&&a.getClientRects().length?a.getAttribute('href'):null; })()")
    if lk: J("document.querySelector('a[data-frota-link]').click()"); time.sleep(2.0)
    ctx = J("sessionStorage.getItem('mapa-ctx')"); rec = J("(document.querySelector('.fr-recorte')||{}).innerText||''"); h2 = J("(document.querySelector('[data-frota-painel] h2')||{}).innerText||''")
    chk('M12 "Ver no mapa" (1 clique) abre o Mapa com o conjunto selecionado; faixa "Recorte temporário" e mapa-ctx inalterado',
        lk == 'IN-04.dc.html#frota=OS-0421' and 'Recorte temporário: OS-0421' in rec and 'Trator 03' in h2 and json.loads(ctx or '{}').get('mf_faz') == 'Lagoa Grande', [lk, rec, h2, ctx])
try:
    # ---------------- Santa Rita, Ana
    abre()
    tem = J("!!document.querySelector('[data-frota-tog]')")
    if not tem:   # contraprova (M22): render de antes da F1, sem alternador; reprova caso a caso em vez de parar com exceção
        chk('M1 Santa Rita: "Máquinas (2)"; 1 marcador (OS-0421)', False, 'sem o alternador Máquinas')
        chk('M2 1 clique liga e o seguinte desliga', False, 'sem o alternador Máquinas')
        chk('M3 1 toque no marcador abre o painel', False, 'sem marcador: ' + str(J("document.querySelectorAll('[data-frota-os]').length")))
        m12()
        raise Pare
    t0 = J("(document.querySelector('[data-frota-tog]')||{}).innerText||''")
    liga(); mk = json.loads(J(MK) or '[]'); ls = lista()
    em_exec = J("JSON.stringify(Object.values(window.__frotaTeste.cenario().ordens).filter(o=>o.etapa==='Em execução').map(o=>o.id).sort())")
    chk('M1 Santa Rita: "Máquinas (2)"; lista OS-0420 e OS-0421 (os Em execução do cenário nesta fazenda); 1 marcador (OS-0421)', tem and 'Máquinas (2)' in t0 and [r[2] for r in ls] == ['OS-0420', 'OS-0421'] and [m['os'] for m in mk] == ['OS-0421'] and set(['OS-0420', 'OS-0421']) <= set(json.loads(em_exec or '[]')), [t0, ls, mk, em_exec])
    # M3 painel
    J("document.querySelector('[data-frota-painel] .fr-x')&&document.querySelector('[data-frota-painel] .fr-x').click()"); time.sleep(.4)
    J("document.querySelector('[data-frota-os=\"OS-0421\"]').click()"); time.sleep(.6)
    pn = J(PAINEL); href = J("(document.querySelector('[data-frota-painel] .fr-prim')||{}).getAttribute&&document.querySelector('[data-frota-painel] .fr-prim').getAttribute('href')")
    campos = ['O.S. e versão', 'Operação', 'Talhão', 'Conjunto', 'Estado', 'Posição', 'Quanto falta', 'Operador']
    chk('M3 1 toque no marcador abre o painel com os campos da decisão 9; "Abrir O.S." vai à OS-0421',
        all(x in pn for x in campos) and 'Trator 03 + Pulverizador PJ-3030' in pn and '190 de 350 ha apontados · saldo 160 ha' in pn and '≈ 7,4 h' in pn
        and '6 cargas de 30 ha, a última com 10 ha' in pn and 'Marcos' in pn and href == 'OS.dc.html#OS-0421'
        and 'OS-0421 · v2' in pn and not re.search(r'\bvv\d', pn), [pn, href])   # versão sem prefixo duplicado ('vv2', achado da foto de 19/10)
    # M15 mesma fonte e idade no mapa, lista e painel
    al = (json.loads(J(MK) or '[]') or [{}])[0].get('al', '')
    ida = re.search(r'leitura (há [^·]+?)(?: ·|$)', al); ida = ida.group(1).strip() if ida else '?'
    chk('M15 marcador e painel com a mesma fonte (simulação) e a mesma idade', 'simulação' in al and ida in pn and 'fonte: simulação' in pn, [al, ida])
    # M10 Esc devolve o foco ao marcador
    J("document.querySelector('[data-frota-painel] h2').focus()"); c.tecla('Escape', 'Escape', 27); time.sleep(.5)
    foco = J("document.activeElement&&document.activeElement.getAttribute('data-frota-os')")
    chk('M10 Esc fecha o painel e devolve o foco ao marcador de origem', foco == 'OS-0421' and not J("!!document.querySelector('[data-frota-painel] h2')"), foco)
    # M4 a posição simulada está dentro do T2
    dentro = J("""(()=>{ const b=document.querySelector('[data-frota-os="OS-0421"]'); const r=b.getBoundingClientRect(); const x=r.left+r.width/2, y=r.top+r.height/2;
      const poly=document.querySelector('svg[data-mux-grupo] [data-talhao="T2"]'); const svg=poly.ownerSVGElement; const p=svg.createSVGPoint(); p.x=x; p.y=y;
      const q=p.matrixTransform(svg.getScreenCTM().inverse()); return poly.isPointInFill?poly.isPointInFill(q):null; })()""")
    chk('M4 a posição simulada da OS-0421 está dentro do T2; a OS-0420, sem fonte, não tem marcador', dentro is True and not J("!!document.querySelector('[data-frota-os=\"OS-0420\"]')"), dentro)
    # M18/M19 legenda e marca de simulação; nenhum "telemetria" na tela
    leg = J("(document.querySelector('[data-frota-leg]')||{}).innerText||''"); m0 = (json.loads(J(MK) or '[]') or [{}])[0]
    chk('M18 marcador com ícone, rótulo curto e selo com palavra; legenda com ícones e estados', m0.get('ic') and 'T03 · Pulverização' in m0.get('txt', '') and re.search(r'(trabalhando|parada)', m0.get('txt', ''))
        and 'Pulverização' in leg and '▶ trabalhando' in leg and '◌ sem sinal' in leg, [m0, leg])
    chk('M19 "Posições simuladas · demonstração" na legenda e nenhuma posição chamada de telemetria', 'Posições simuladas · demonstração' in leg and 'telemetria' not in J("document.body.innerText").lower(), leg)
    # M2 + M20: nove funções, liga e desliga, estado do mapa igual
    funcs = json.loads(J("JSON.stringify([...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].map(b=>b.innerText.trim()).filter(Boolean))") or '[]')
    snap = "JSON.stringify({sel:[...document.querySelectorAll('svg[data-mux-grupo] [data-talhao]')].map(e=>[e.getAttribute('data-talhao'),e.getAttribute('fill'),e.getAttribute('aria-pressed')]), num:(document.querySelector('.mapa-num')||{}).innerText, faixa:(document.querySelector('.mapa-faixa b')||{}).innerText})"
    m2 = []
    J("document.querySelector('svg[data-mux-grupo] [data-talhao=\"T4\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); time.sleep(.4)
    for fn in funcs:
        J("(()=>{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].find(b=>b.innerText.trim()===%s); if(b) b.click();})()" % json.dumps(fn)); time.sleep(.5)
        J("(()=>{const b=document.querySelector('[data-frota-tog]'); if(b.getAttribute('aria-pressed')==='true') b.click();})()"); time.sleep(.4)
        a = J(snap); J("document.querySelector('[data-frota-tog]').click()"); time.sleep(.5); on = J("document.querySelector('[data-frota-tog]').getAttribute('aria-pressed')"); b = J(snap)
        J("document.querySelector('[data-frota-tog]').click()"); time.sleep(.4); off = J("document.querySelector('[data-frota-tog]').getAttribute('aria-pressed')"); d = J(snap)
        m2.append((fn, on == 'true' and off == 'false', a == b == d))
    chk('M2 nas nove funções: 1 clique liga e o seguinte desliga (aria-pressed acompanha)', len(funcs) == 9 and all(x[1] for x in m2), m2)
    chk('M20 cores, seleção do talhão (T4) e números da faixa iguais antes, com e depois de Máquinas, nas nove funções', all(x[2] for x in m2), [x for x in m2 if not x[2]])
    # M5 corte de sinal com relógio de teste
    abre(extra="window.name='';")
    t = (J("window.__frotaTeste.agora()") // 10) * 10   # alinhado à leitura de 10 s: a última leitura antes do corte tem exatamente 60 s de idade
    J("window.__frotaRelogio=%d; window.__frotaFixture={'OS-0421':{corte:%d}}; 1" % (t, t - 60)); liga()
    a60 = (json.loads(J(MK) or '[]') or [{}])[0]
    J("window.__frotaRelogio=%d; window.__frotaTeste.redesenha(); 1" % (t + 1)); time.sleep(.3)
    a61 = (json.loads(J(MK) or '[]') or [{}])[0]; ls61 = lista()
    chk('M5 fronteira: 60 s Atual (sólido); 61 s "Sem sinal há 1 min", vazado, sem seta, sem "parada"',
        a60.get('vaz') is False and a61.get('vaz') is True and not a61.get('seta') and any('Sem sinal há 1 min' in r[5] for r in ls61) and 'parada' not in (a61.get('txt') or '').lower(), [a60, a61, ls61])
    # M7 pausa sem leitura + M24 leitura contradiz o impedimento
    J("window.__frotaRelogio=null; window.__frotaFixture={'OS-0421':{semFonte:true}}; window.__frotaTeste.redesenha(); 1"); time.sleep(.3)
    ls7 = lista(); mk7 = json.loads(J(MK) or '[]')
    chk('M7 sem leitura: a O.S. fica na lista, sem marcador; a impedida mostra o selo e "estado desconhecido"', [r[2] for r in ls7] == ['OS-0420', 'OS-0421'] and not mk7
        and any('impedida' in r[4].lower() and 'estado desconhecido' in r[4] for r in ls7), [ls7, mk7])
    J("(()=>{ const F=window.__frotaTeste.frota0(); F.simula.push('OS-0420'); F.rota_tal['OS-0420']='T4'; window.__frotaFixture={}; window.__frotaTeste.estado('frSel','OS-0420'); })(); 1"); time.sleep(.8)
    p24 = J(PAINEL)
    chk('M24 leitura "Trabalhando" numa O.S. impedida: aviso para conferir; o selo da O.S. continua', 'Leitura contradiz o impedimento da O.S. · conferir' in p24 and 'Impedida · ativo bloqueado' in p24, p24)
    # M8 conflito ao iniciar a OS-0424 (estado gravado editado como o comando faria, só a etapa)
    abre()
    J("window.__frotaTeste.cenario(c=>{ c.ordens['OS-0424'].etapa='Em execução'; }); 1")   # só a etapa, como o comando Iniciar deixaria
    c.goto('about:blank', .1); c.goto(U('IN-04.dc.html'), 1.2); liga(); ls8 = lista()
    chk('M8 iniciar a OS-0424: o PJ-3030 nas duas O.S.; as linhas dizem "Conflito · também na OS-…"',
        any(r[2] == 'OS-0421' and 'Conflito · também na OS-0424' in r[4] for r in ls8) and any(r[2] == 'OS-0424' and 'Conflito · também na OS-0421' in r[4] for r in ls8), ls8)
    # M9 sai de Em execução com o painel aberto
    abre(); liga(); J("document.querySelector('[data-frota-os=\"OS-0421\"]').click()"); time.sleep(.5)
    J("window.__frotaTeste.cenario(c=>{ c.ordens['OS-0421'].etapa='Em conferência'; }); window.__frotaTeste.render(); 1"); time.sleep(.8)
    p9 = J(PAINEL)
    chk('M9 enviada para conferência com o painel aberto: o marcador sai e o painel avisa', 'saiu de Em execução (agora Em conferência)' in p9 and not J("!!document.querySelector('[data-frota-os=\"OS-0421\"]')"), p9)
    m12()
    # M13 Rui
    abre(perfil='Rui'); liga(); ls13 = lista()
    tudo = J("document.body.innerText+' '+[...document.querySelectorAll('[aria-label],[title],[data-dica]')].map(e=>(e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')+' '+(e.getAttribute('data-dica')||'')).join(' ')")
    chk('M13 Rui: só a lista, "Posição restrita ao seu perfil", sem marcador, operador, idade ou coordenada', not json.loads(J(MK) or '[]') and len(ls13) == 2
        and all('Posição restrita ao seu perfil' in r[5] for r in ls13) and not re.search(r'Marcos|Carlos|há menos de 1 min|leitura há|-34\.6|-47\.1', tudo), [ls13])
    # M14 sem efeito no domínio
    abre(); antes = foto_estado(); liga()
    for i in range(10): J("document.querySelector('[data-frota-tog]').click()"); time.sleep(.25)
    time.sleep(30); c.goto('about:blank', .1); c.goto(U('IN-04.dc.html'), 1.0); liga(); time.sleep(2)
    depois = foto_estado()
    chk('M14 30 s de leituras, ligar e desligar 10 vezes e recarregar: o cenário gravado fica igual byte a byte', antes == depois, [len(antes or ''), len(depois or '')])
    erros.extend(J("window.__e") or [])
    # ---------------- Lagoa Grande
    abre(faz='Lagoa Grande', perfil='Caio'); liga(); mkl = json.loads(J(MK) or '[]'); lsl = lista()
    chk('M1 Lagoa Grande: lista OS-0505, OS-0506 e OS-0507 (ativos fixos "ver na Irrigação"); 1 marcador (OS-0505, conjunto de demonstração)',
        [r[2] for r in lsl] == ['OS-0505', 'OS-0506', 'OS-0507'] and [m['os'] for m in mkl] == ['OS-0505'] and all('Ativo fixo · ver na Irrigação' in r[5] for r in lsl[1:]), [lsl, mkl])
    erros.extend(J("window.__e") or [])
    # ---------------- M16 390 px com toque e 1440 px
    res16 = {}
    for w, h, toque in ((1440, 900, False), (390, 844, True)):
        abre(w=w, h=h, toque=toque); liga()
        al = json.loads(J("JSON.stringify(['[data-frota-tog]','[data-frota-lista]','[data-frota-os]'].map(s=>{const b=document.querySelector(s); if(!b) return null; const r=b.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height)];}))") or '[]')
        lat = J("document.documentElement.scrollWidth>innerWidth+1"); res16[w] = (al, lat); erros.extend(J("window.__e") or [])
    chk('M16 alternador, Lista e marcador com alvo ≥ 44 px a 390 (toque); sem rolagem lateral a 1440 e 390', all(x and x[0] >= 44 and x[1] >= 44 for x in res16[390][0]) and not res16[390][1] and not res16[1440][1], res16)
    chk('M16 nenhum erro de JavaScript', not erros, erros[:5])
except Pare:
    pass
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok')
sys.exit(1 if FAIL else 0)
