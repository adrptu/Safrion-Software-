# -*- coding: utf-8 -*-
"""Cadastros no padrão comum (proprietário, 16/10/2026: "todas telas de cadastro estao fora do nosso padrão"; skill padrao-safrion, passo 6).
Protege o que a frente CADASTROS-PADRAO mudou, nas telas CD-01 a CD-08 (e CD-01det), em 1440 px:
  P1  nenhuma regra de CSS da área mira classe do motor (ds_inventario: cadastros.py e cad_*.py com css 0) e não há faixa de cartões
      "precisa de atenção" nem cartões próprios (TAB-06, TAB-07, VIS-05)
  P2  cabeçalho da tabela no desenho do motor (maiúsculas pequenas e apagadas) e a tabela na caixa do motor (g2caixa dentro do bloco)
  P3  BOT-01/03/05: a única primária verde fica no cabeçalho da tela, à direita do título, com o verbo Criar e o "+"; nada verde no bloco;
      com abas, o rótulo segue a aba e a aba que não cria fica sem verde
  P4  TAB-01: barra da grade numa linha; busca e filtro rápido (no lugar do motor) à esquerda; Colunas e Tabela | Cartões na ponta direita;
      na tela com o seletor de visões (VIS-08, CD-01), o Tabela | Cartões fica nele, acima da lista, e sai da barra;
      TAB-02: sem "x de y" com filtro rápido
  P5  CD-01 (16/10: "fazendas e talhoes na mesma tela, conectados e intuitivos"): uma árvore só; a fazenda é a linha-pai e abre o painel
      dela; a seta abre e fecha; a área cultivável da fazenda é a soma dos talhões ativos; Criar fazenda e Incluir talhão funcionam
  P6  formulários só com o essencial e documentos para crédito no Crédito (GE-08 › Documentos para crédito), com os mesmos dados
Contraprova: CONTRAPROVA=1 RENDER_DIR=<_render da base 6a23a88> inverte o resultado (a base tem de reprovar P1 a P4 e P6).
Uso (de gen37/, depois do build): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B cadastros_padrao_test.py"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import dados_cad as DC

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
CONTRA = os.environ.get('CONTRAPROVA') == '1'
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome.split(' ')[0]); print('FALHA ' + nome + ' · ' + str(det)[:400], flush=True)

TELAS = ['CD-01.dc.html', 'CD-02.dc.html', 'CD-03.dc.html', 'CD-04.dc.html', 'CD-05.dc.html', 'CD-06.dc.html', 'CD-07.dc.html', 'CD-08.dc.html']
# ---- P1 (fonte): CSS da área sobre o motor e peças próprias que imitam o motor ----
if not CONTRA:
    import ds_inventario as INV
    inv = INV.varre()
    cad = {n: v for n, v in inv.items() if n == 'cadastros.py' or n.startswith('cad_')}
    chk('P1a CSS da área sobre classe do motor: 0 regras nos cadastros (antes 15 no CADX_CSS)', all(v['css'] == 0 and v['cartao'] == 0 for v in cad.values()), cad)
html = {t: open(os.path.join(R, t), encoding='utf-8').read() for t in TELAS + ['CD-01det.dc.html']}
proprias = {t: [k for k in ('cadx-faixa', 'cadx-aviso', 'cadx-cartao', '.cadx .g2hb', 'cadx-prim') if k in s] for t, s in html.items()}
chk('P1b sem faixa "precisa de atenção", cartões próprios nem primária na barra (TAB-06/07, VIS-05)', not any(proprias.values()), {k: v for k, v in proprias.items() if v})

# ---- navegador ----
p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda x: f'http://127.0.0.1:{p}/{x}'
def ir(url, limpa=True):
    if limpa:
        c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    c.goto(U(url), 1.4)
def espera(cond, lim=6.0):
    t0 = time.time()
    while time.time() - t0 < lim:
        if J("(()=>{try{return !!(%s)}catch(e){return false}})()" % cond): return True
        time.sleep(.15)
    return False
VERDES = r"""(()=>{ const vis=e=>{ const r=e.getBoundingClientRect(); return r.width>1&&r.height>1&&getComputedStyle(e).visibility!=='hidden'; };
  const verde=e=>getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)'&&!e.closest('.menu-lat,[role=tablist],[role=group],[role=toolbar],.g2visoes');
  const h=[...document.querySelectorAll('header button,header a')].filter(e=>vis(e)&&verde(e)), m=[...document.querySelectorAll('main button,main a')].filter(e=>vis(e)&&verde(e));
  const h1=document.querySelector('header h1'); const dir=h.length&&h1?h[0].getBoundingClientRect().left>h1.getBoundingClientRect().right:false;
  return {h:h.map(e=>e.innerText.trim()), m:m.map(e=>e.innerText.trim()), dir, mais:h.length?!!h[0].querySelector('svg'):false}; })()"""
BARRA = r"""(()=>{ const cx=[...document.querySelectorAll('.g2caixa')].find(x=>x.offsetParent&&x.querySelector('[role=table],.g2cartoes')); if(!cx) return null;
  const b=cx.firstElementChild; const kids=[...b.children].filter(e=>{ const r=e.getBoundingClientRect(); return r.width>1&&r.height>1; });
  const tx=e=>(e.innerText||'').replace(/\s+/g,' ').trim();
  const tipo=e=>{ if(e.querySelector('input[type=search]')) return 'busca'; if(e.matches('.g2modos')||e.querySelector('.g2modos')) return 'modos';
    if(e.matches('[role=group]')&&e.querySelector('[aria-pressed]')) return 'filtro'; if(e.matches('label')&&e.querySelector('select')) return 'filtro';
    if(/^Colunas/.test(tx(e))) return 'colunas'; if(/Agrupar por/.test(tx(e))) return 'agrupar'; if(/^(Expandir|Recolher) tudo/.test(tx(e))) return 'expandir';
    if(/^\d+ de \d+$/.test(tx(e))) return 'conta'; return 'ferramenta'; };
  const tops=kids.map(e=>Math.round(e.getBoundingClientRect().top+e.getBoundingClientRect().height/2));
  const hb=cx.querySelector('.g2hb'); return {visoes:!!document.querySelector('[data-visoes-gid] [data-visao=cartoes]'), ordem:kids.map(tipo), linhas:new Set(tops.map(t=>Math.round(t/8))).size, umaLinha:Math.max(...tops)-Math.min(...tops)<=6,
    caixa:getComputedStyle(hb||b).textTransform, hbCor:hb?getComputedStyle(hb).color:'', blocoCaixa:!!cx.closest('section')}; })()"""
try:
    c.aparelho(1440, 900, 1, False)
    PRIM = {'CD-01.dc.html': 'Criar fazenda', 'CD-02.dc.html': 'Criar cultivar', 'CD-03.dc.html': 'Criar máquina ou instalação', 'CD-04.dc.html': 'Criar pessoa',
            'CD-05.dc.html': 'Criar parceiro', 'CD-06.dc.html': 'Criar item', 'CD-07.dc.html': 'Criar código', 'CD-08.dc.html': 'Criar rendimento'}
    for t in TELAS:
        ir(t)
        v = J(VERDES); b = J(BARRA) or {}
        chk(f'P3 {t}: a única primária é "{PRIM[t]}", no cabeçalho à direita do título, com o "+"; nada verde no bloco (BOT-01/03/05)',
            v['h'] == [PRIM[t]] and v['dir'] and v['mais'] and not v['m'], v)
        o = b.get('ordem') or []
        # TAB-01: à esquerda a busca e os filtros (um ou mais seguidos); à direita, nesta ordem: ferramentas da tela, Expandir tudo, Agrupar por,
        # Colunas e Tabela | Cartões na ponta; TAB-02: sem "x de y" com filtro rápido
        nf = next((i for i, x in enumerate(o[1:], 1) if x != 'filtro'), len(o)); dire = o[nf:]
        ORD = ['ferramenta', 'expandir', 'agrupar', 'colunas', 'modos']
        esq_ok = o[:1] == ['busca'] and nf >= 2 and 'conta' not in o
        # VIS-08 (18/10/2026): na tela com o seletor de visões da VISOES-1 (CD-01: Tabela · Cartões · Mapa, acima da lista, como na IR-01),
        # o Tabela | Cartões sai da barra da tabela; a barra termina no Colunas e não repete os modos
        fim_ok = bool(dire) and (dire[-1] == 'modos' if not b.get('visoes') else 'modos' not in dire)
        dir_ok = bool(dire) and fim_ok and all(x in ORD for x in dire) and [ORD.index(x) for x in dire] == sorted(ORD.index(x) for x in dire)
        chk(f'P4 {t}: barra numa linha, busca e filtro rápido à esquerda, Colunas e Tabela | Cartões na ponta (TAB-01/02)', b.get('umaLinha') and esq_ok and dir_ok, b)
        chk(f'P2 {t}: cabeçalho da tabela em maiúsculas pequenas e apagadas e tabela na caixa do motor dentro do bloco', b.get('caixa') == 'uppercase' and b.get('hbCor') == 'rgb(101, 115, 106)' and b.get('blocoCaixa'), b)
    # com abas, o rótulo segue a aba; a aba que não cria fica sem verde
    for t, aba, rot in [('CD-03.dc.html', 'conjuntos', ['Criar conjunto']), ('CD-04.dc.html', 'equipes', ['Criar equipe']), ('CD-06.dc.html', 'locais', ['Criar local']),
                        ('CD-05.dc.html', 'cobertura', []), ('CD-01.dc.html', 'agua', [])]:
        ir(t + '#aba=' + aba); v = J(VERDES)
        chk(f'P3 {t} aba {aba}: primária do cabeçalho = {rot or "nenhuma"}', v['h'] == rot and not v['m'], v)
    # Equipes e Conjuntos: grade do motor com Tabela | Cartões (antes só cartões próprios)
    for t, aba, nome in [('CD-03.dc.html', 'conjuntos', 'Trator 02 + Pulverizador PJ-3030'), ('CD-04.dc.html', 'equipes', 'Campo 1')]:
        ir(t + '#aba=' + aba)
        r = J("(()=>{ const cx=[...document.querySelectorAll('.g2caixa')].find(x=>x.offsetParent); return cx?{linha:[...cx.querySelectorAll('[role=row]')].some(r=>r.innerText.indexOf(%s)>=0), modos:!!cx.querySelector('.g2modos button[data-modo=cartoes]')}:null; })()" % json.dumps(nome))
        chk(f'P1c {t} {aba}: a lista é a grade do motor com Tabela | Cartões (VIS-05)', r and r['linha'] and r['modos'], r)

    # ---- P5: CD-01 numa árvore só ----
    ir('CD-01.dc.html')
    ROW = "[...document.querySelectorAll('[role=table] [role=row]')].find(r=>(r.querySelector('[role=cell]')||{innerText:''}).innerText.replace(/\\s+/g,' ').replace(/^[▾▸]\\s*/,'').trim().startsWith(%s))"
    cab = J("[...document.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▲▼]/g,'').replace(/\\s+/g,' ').trim().toLowerCase())") or []
    ic = cab.index('área cultivável') if 'área cultivável' in cab else -1
    cel = lambda nome: J("(()=>{ const r=%s; return r?[...r.querySelectorAll('[role=cell]')].map(c=>c.innerText.replace(/\\s+/g,' ').trim()):null; })()" % (ROW % json.dumps(nome)))
    num = lambda s: float(s.replace(' ha', '').replace('.', '').replace(',', '.')) if s else 0.0
    # TAB-12 (17/10): a fazenda nasce recolhida; a seta abre os talhões (soma conferida aberta) e recolhe de novo (base verde 2, 18/10)
    exp0 = J("(()=>{ const r=%s; const b=r&&r.querySelector('.g2car'); return b?b.getAttribute('aria-expanded'):null; })()" % (ROW % '"Santa Rita"'))
    fechada0 = cel('T1') is None
    J("(()=>{ const r=%s; const b=r&&r.querySelector('.g2car'); if(b) b.click(); })()" % (ROW % '"Santa Rita"')); time.sleep(.4); abriu = cel('T1') is not None
    sr = cel('Santa Rita') or []; kids = ['T1', 'T2', 'T3', 'T4', 'P1', 'P2', 'T7', 'C1']; soma = round(sum(num((cel(k) or [''] * 9)[ic]) for k in kids), 1)
    chk('P5a fazenda é a linha-pai da árvore (Santa Rita com empresa e município), com a soma da área cultivável dos talhões ativos',
        sr and 'Santa Rita Agro' in sr[0] and 'Rio Verde/GO' in sr[0] and ic > 0 and abs(num(sr[ic]) - soma) < 0.05 and soma > 0, [sr, ic, soma])
    J("(()=>{ const r=%s; const b=r&&r.querySelector('.g2car'); if(b) b.click(); })()" % (ROW % '"Santa Rita"')); time.sleep(.4); fechou = cel('T1') is None
    chk('P5b a fazenda nasce recolhida (TAB-12) e a seta abre e recolhe os talhões', exp0 == 'false' and fechada0 and abriu and fechou, [exp0, fechada0, abriu, fechou])
    J("(()=>{ const r=%s; if(r) (r.querySelector('.g2pw')||r).click(); })()" % (ROW % '"Boa Vista"')); espera("document.querySelector('aside[role=dialog]')")
    tit = J("(document.querySelector('aside[role=dialog] h2')||{}).innerText||''"); lb = J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())") or []
    acts = J("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim())") or []
    chk('P5c clicar na fazenda abre o painel da fazenda, com "Incluir talhão" e o vínculo "Documentos para crédito ›"', 'Boa Vista' in tit and 'Incluir talhão' in acts and 'Documentos para crédito ›' in acts, [tit, acts])
    FORA = ['CAR', 'Matrícula e cartório', 'Módulos fiscais', 'Fuso horário', 'Custo da terra', 'Arrendador ou parceiro', 'Pendência nos documentos', 'Perímetros']
    chk('P6a formulário da fazenda só com o essencial (sem CAR, matrícula, módulos fiscais, fuso, custo da terra, arrendador)', lb and not [x for x in FORA if x in lb] and 'Posse' in lb, lb)
    # Criar fazenda (cabeçalho) e Incluir talhão (painel da fazenda)
    ir('CD-01.dc.html')
    J("(()=>{ const b=[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Criar fazenda'); if(b) b.click(); })()"); espera("document.querySelector('aside[role=dialog]')")
    SETV = "((sel,val)=>{const i=document.querySelector(sel); if(!i) return false; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event(i.tagName==='SELECT'?'change':'input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return true;})"
    def fset(k, val): J("(%s)('aside[role=dialog] [id$=\"_%s\"]',%s)" % (SETV, k, json.dumps(val))); time.sleep(.15)
    def btn(t): J("(()=>{ const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===%s); if(b) b.click(); })()" % json.dumps(t)); time.sleep(.4)
    fset('nome', 'Fazenda Teste'); fset('mun', 'Jataí'); fset('area', '500'); btn('Salvar')
    nova = cel('Fazenda Teste')
    chk('P5d "Criar fazenda" grava a fazenda e ela vira uma linha-pai da árvore', bool(nova) and not J("!!document.querySelector('aside[role=dialog]')"), nova)
    J("(()=>{ const r=%s; if(r) (r.querySelector('.g2pw')||r).click(); })()" % (ROW % '"Fazenda Teste"')); espera("document.querySelector('aside[role=dialog]')")
    btn('Incluir talhão'); espera("(document.querySelector('aside[role=dialog] h2')||{}).innerText==='Cadastrar talhão'")
    faz = J("(document.querySelector('aside[role=dialog] [id$=\"_faz\"]')||{}).value")
    fset('t', 'X1'); fset('decl', '100'); btn('Salvar'); time.sleep(.3)
    pai = cel('Fazenda Teste') or []; filho = cel('X1')
    chk('P5e "Incluir talhão" abre o talhão já na fazenda; salvo, ele entra sob ela e soma na área cultivável dela',
        faz == 'Fazenda Teste' and bool(filho) and ic > 0 and len(pai) > ic and num(pai[ic]) == 100.0, [faz, filho, pai])
    chk('P5f sem erro de JS no CD-01', not J("(window.__e||[]).length"), J("window.__e"))

    # ---- P6: formulários essenciais e documentos no Crédito ----
    ir('CD-05.dc.html')
    J("(()=>{ const b=[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Criar parceiro'); if(b) b.click(); })()"); espera("document.querySelector('aside[role=dialog]')")
    J("(()=>{ const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==='Parceiro de crédito'); if(l) l.click(); })()"); time.sleep(.3)
    J("(()=>{ const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==='Cliente'); if(l) l.click(); })()"); time.sleep(.3)
    lb5 = J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())") or []
    FORA5 = ['Garantias aceitas', 'Gerente do crédito', 'E-mail do gerente', 'Telefone do gerente', 'Produtos de interesse', 'Local e horário de entrega', 'Condição de pagamento']
    chk('P6b parceiro: Cliente e Parceiro de crédito só com o essencial (limite e validade; linhas de crédito)', 'Linhas de crédito' in lb5 and 'Limite de crédito comercial' in lb5 and not [x for x in FORA5 if x in lb5], lb5)
    ir('CD-04.dc.html')
    J("(()=>{ const b=[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Criar pessoa'); if(b) b.click(); })()"); espera("document.querySelector('aside[role=dialog]')")
    lb4 = J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())") or []
    chk('P6c pessoa sem "Calendário de trabalho" (vale o da equipe)', lb4 and 'Calendário de trabalho' not in lb4 and 'Equipe' in lb4, lb4)
    ir('GE-08.dc.html#vis=documentos')
    linhas = J("[...document.querySelectorAll('[role=table] [role=row]')].filter(r=>r.offsetParent).map(r=>r.innerText.replace(/\\s+/g,' ').trim())") or []
    fz = {f['id']: f for f in DC.FAZENDAS}
    tem = lambda *xs: any(all(x in l for x in xs) for l in linhas)
    chk('P6d Crédito › Documentos para crédito com o CAR e a matrícula da Santa Rita, o contrato de arrendamento da Boa Vista e o CAR da Lagoa Grande (mesmos dados)',
        tem('CAR', 'Santa Rita', fz['SR']['car']) and tem('Matrícula', 'Santa Rita', fz['SR']['matr']) and tem('Contrato de arrendamento', 'Boa Vista', 'Pendente', '31/08/2029')
        and tem('CAR', 'Lagoa Grande', fz['LG']['car']) and tem('CAR', 'Boa Vista', 'Pendente'), linhas)
    chk('P6e sem erro de JS no Crédito', not J("(window.__e||[]).length"), J("window.__e"))
finally:
    c.close(); srv.terminate()
n = ok_n + len(falhas)
if CONTRA:
    # a base tem de reprovar o que a frente mudou (P1 a P4 e P6); P5 não existe na base
    caiu = {f[:2] for f in falhas}
    ok = {'P1', 'P2', 'P3', 'P4', 'P6'} <= caiu
    print(f'RESULTADO (contraprova): {"ok, a base reprova " + ", ".join(sorted(caiu)) if ok else "FALHOU: a base passou em " + ", ".join(sorted({"P1","P2","P3","P4","P6"} - caiu))} · {ok_n}/{n} verificações passaram na base')
    sys.exit(0 if ok else 1)
print(f'RESULTADO: {ok_n}/{n}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
