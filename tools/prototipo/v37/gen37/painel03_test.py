# -*- coding: utf-8 -*-
"""PAINEL-03 · painel de gestão único (PG.dc.html), aceite P1–P8 de docs/painel03/README.md. Chrome a 1440 × 900 e a 390 × 844 (toque).
  P1 o item Painel da barra abre Prioridades; o Painel de cada módulo (tela de entrada e menu) abre a aba dele; PAGR, PMAN e PSUP saíram e
     nenhuma página aponta para elas
  P2 os indicadores das abas usam as mesmas contas dos painéis antigos: fases (pnValores), atrasadas e impedidas (agrPainelRef), Manutenção e
     Estoque (pnValores), custo (agrCustoRef)
  P3 "Atacar agora": classe do dano, depois R$, ha e dias, depois o mais antigo; nenhum item duplicado; a O.S. impedida e atrasada vira um item
  P4 coleção ausente = "Sem dados", nunca 0
  P5 o painel lê e não grava (cenário e armazenamento iguais antes e depois de navegar pelas abas)
  P6 número da aba = itens a atacar e decidir do módulo; some com 0
  P7 1440 e 390: nada vaza na largura; abas com 44 px; setas, Home e End trocam a aba e levam o foco; dica ⓘ em cada cartão; sem erro de JS
  P8 Comercial: o Painel do módulo é a aba; a tela de oferta virou "Oferta e compromissos" (título = item do menu)
Contraprova: RENDER_DIR=<render da v133> reprova P1 (PG ausente; PAGR/PMAN/PSUP no menu).
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B painel03_test.py"""
import os, sys, json, time, glob, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:600])

# ---------- P1 (arquivos): páginas antigas fora e nenhum link para elas ----------
ANTIGAS = ('PAGR.dc.html', 'PMAN.dc.html', 'PSUP.dc.html')
pags = sorted(glob.glob(os.path.join(R, '*.dc.html')))
chk('P1a PG.dc.html existe e PAGR, PMAN e PSUP saíram', os.path.exists(os.path.join(R, 'PG.dc.html')) and not any(os.path.exists(os.path.join(R, a)) for a in ANTIGAS),
    [os.path.basename(p) for p in pags if os.path.basename(p) in ANTIGAS + ('PG.dc.html',)])
lig = sorted({(os.path.basename(p), a) for p in pags for a in ANTIGAS if a in open(p, encoding='utf-8', errors='ignore').read()})
chk('P1b nenhuma página aponta para PAGR, PMAN ou PSUP', not lig, lig[:6])

port, srv = servir(R); c = Chrome(); J = c.js
U = lambda f: f'http://127.0.0.1:{port}/{f}'
def espera(cond, s=8):
    fim = time.time() + s
    while time.time() < fim:
        try:
            if J(cond): return True
        except Exception: pass
        time.sleep(.15)
    return False
ABA = "JSON.stringify([...document.querySelectorAll('[role=tab][data-pg]')].map(b=>[b.getAttribute('data-pg'),b.getAttribute('aria-selected'),(b.querySelector('.pg-n')&&!b.querySelector('.pg-n').hidden&&getComputedStyle(b.querySelector('.pg-n')).display!=='none')?b.querySelector('.pg-n').innerText.trim():'']))"
def abas(): return json.loads(J(ABA) or '[]')
def sel(): return next((a[0] for a in abas() if a[1] == 'true'), None)
try:
    for W, Hh, toque in ((1440, 900, False), (390, 844, True)):
        tag = str(W); c.aparelho(W, Hh, toque=toque)
        c.goto(U('PG.dc.html'), 1.4); J("window.__errs=window.__errs||[]")
        espera("!!window.__pg&&document.querySelectorAll('[role=tab][data-pg]').length===6")
        if W == 1440:
            # ---------- P2–P5 (contas, na página real) ----------
            u = json.loads(J(r"""JSON.stringify((()=>{const P=window.__pg; if(!P) return null; const c=P.cenClone(P.CEN0), antes=JSON.stringify(c);
              const R=P.pgDados(c), pa=P.pnValores(c,'PAGR'), pm=P.pnValores(c,'PMAN'), ps=P.pnValores(c,'PSUP'), ref=P.agrPainelRef(c,{}), cu=P.agrCustoRef(c,{});
              const v=b=>b.map(k=>k.v), num=x=>x===null?'Sem dados':x.toLocaleString('pt-BR');
              const ks=R.itens.map(x=>x.k);
              const ord=R.itens.every((x,i)=>i===0||P.pgOrdem(R.itens[i-1],x)<=0);
              const nulo=P.pgDados({}), vazio=Object.keys(nulo.blocos).filter(m=>m!=='cre').flatMap(m=>Object.values(nulo.blocos[m]).flat()).filter(k=>k.v==='0');   /* a ficha do Crédito não vem do cenário (é do armazenamento do Crédito) */
              return {erro:R.erro||null, agr:v(R.blocos.agr.os).slice(0,4), pagr:pa.vals.map(num), atr:R.blocos.agr.os[4].v, imp:R.blocos.agr.os[5].v,
                ratr:num(ref.os.n.atrasadas), rimp:num(ref.os.n.impedidas), man:[R.blocos.man.sem[0].v,R.blocos.man.oms[0].v,R.blocos.man.oms[1].v,R.blocos.man.atv[0].v], pman:pm.vals.map(num),
                sup:v(R.blocos.sup.est).slice(0,4), psup:ps.vals.map(num), cus:R.blocos.agr.cus.length, rcus:cu.cultivos.length,
                dup:ks.length-new Set(ks).size, ord, n:R.itens.length, igual:JSON.stringify(c)===antes,
                nulo:{agr:v(nulo.blocos.agr.os).slice(0,4), man:nulo.blocos.man.sem[0].v, sup:v(nulo.blocos.sup.est).slice(0,4)}, zeros:vazio.map(k=>k.nome),
                classes:R.itens.map(x=>x.classe)};})())""") or 'null')
            chk('P2a Agrícola: as 4 fases são as do pnValores (PAINEL-01)', u and u['agr'] == u['pagr'], u and [u['agr'], u['pagr']])
            chk('P2b Agrícola: atrasadas e impedidas são as do agrPainelRef (PAINEL-02)', u and [u['atr'], u['imp']] == [u['ratr'], u['rimp']], u and [u['atr'], u['imp'], u['ratr'], u['rimp']])
            chk('P2c Manutenção: sem ordem, abertas, em execução e bloqueados = pnValores(PMAN)', u and u['man'] == u['pman'], u and [u['man'], u['pman']])
            chk('P2d Suprimentos: os 4 indicadores do Estoque = pnValores(PSUP)', u and u['sup'] == u['psup'], u and [u['sup'], u['psup']])
            chk('P2e Custos: um cartão por cultivo do agrCustoRef', u and u['cus'] == u['rcus'] and u['cus'] > 0, u and [u['cus'], u['rcus']])
            chk('P3a "Atacar agora" e "Decidir" na ordem da regra (classe, R$, ha, dias, mais antigo) e sem item duplicado', u and u['ord'] and u['dup'] == 0 and u['n'] > 0, u and [u['ord'], u['dup'], u['n'], u['classes']])
            o = json.loads(J(r"""JSON.stringify((()=>{const P=window.__pg, it=(k,cl,imp,d)=>({k,classe:cl,imp,desde:d});
              const xs=[it('a',3,{rs:50000},''),it('b',1,{},''),it('c',2,{dias:9},''),it('d',2,{ha:10},''),it('e',2,{ha:10},'2026-09-01'),it('f',4,{rs:999999},'')].sort(P.pgOrdem);
              return xs.map(x=>x.k);})())""") or '[]')
            chk('P3b ordem: receituário (classe 1) antes de R$ 50 mil (classe 3); na mesma classe, ha antes de dias e o mais antigo primeiro', o == ['b', 'e', 'd', 'c', 'a', 'f'], o)
            chk('P4 coleções ausentes: "Sem dados" em fases, Manutenção e Estoque; nenhum cartão inventa 0', u and u['nulo'] == {'agr': ['Sem dados'] * 4, 'man': 'Sem dados', 'sup': ['Sem dados'] * 4} and not u['zeros'],
                u and [u['nulo'], u['zeros']])
            chk('P5a a conta não altera o cenário', u and u['igual'], u and u['igual'])
            ls0 = J("JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
        # ---------- P1 (navegação) e P6 ----------
        a0 = abas()
        chk(f'P1c {tag}: o painel abre em Prioridades, com as 6 abas', [x[0] for x in a0] == ['pri', 'agr', 'man', 'sup', 'com', 'cre'] and sel() == 'pri', a0)
        cont = json.loads(J("JSON.stringify((()=>{const P=window.__pg; const R=P.pgDados(P.cenGet()); const n={}; R.itens.forEach(x=>{n[x.mod]=(n[x.mod]||0)+1;}); return n;})())") or '{}')
        chk(f'P6 {tag}: número da aba = itens a atacar e decidir do módulo; some com 0 (Prioridades sem número)',
            all((x[2] == (str(cont.get(x[0], 0)) if cont.get(x[0], 0) else '')) for x in a0 if x[0] != 'pri') and a0[0][2] == '', [a0, cont])
        nav = J("(()=>{const a=[...document.querySelectorAll('nav a, aside a, .menu-lat a')].find(x=>x.getAttribute('aria-label')==='Painel'); return a?[a.getAttribute('href'),a.getAttribute('aria-current')]:null;})()")
        chk(f'P1d {tag}: a barra lateral tem o item Painel, marcado nesta tela', nav == ['PG.dc.html', 'page'], nav)
        for m, hub in (('agr', 'MOD-AGR.dc.html'), ('man', 'MOD-MAN.dc.html'), ('sup', 'MOD-SUP.dc.html'), ('com', 'MOD-COM.dc.html'), ('cre', 'MOD-CRE.dc.html')):
            if W == 390 and m not in ('agr', 'cre'): continue
            c.goto(U(hub), 1.0)
            h = J("(()=>{const a=[...document.querySelectorAll('main a')].find(x=>(x.getAttribute('href')||'').indexOf('PG.dc.html')===0); return a?a.getAttribute('href'):null;})()")
            if h: J("(()=>{const a=[...document.querySelectorAll('main a')].find(x=>(x.getAttribute('href')||'').indexOf('PG.dc.html')===0); a.click();})()")
            espera("location.pathname.endsWith('PG.dc.html')&&document.querySelectorAll('[role=tab][data-pg]').length===6"); time.sleep(.5)
            chk(f'P1e {tag} {hub}: o cartão Painel abre o painel único na aba do módulo', h == f'PG.dc.html#mod={m}' and sel() == m, [h, sel()])
        # ---------- P7: teclado, endereço, largura, toque, dica ----------
        c.goto(U('PG.dc.html#mod=man'), 1.2); espera("document.querySelectorAll('[role=tab][data-pg]').length===6")
        chk(f'P7a {tag}: o endereço #mod=man abre a aba Manutenção', sel() == 'man', abas())
        if W == 1440:
            J("document.querySelector('[role=tab][data-pg=man]').focus()"); c.tecla('ArrowRight', 'ArrowRight', 39); time.sleep(.5)
            f1 = [sel(), J("document.activeElement&&document.activeElement.getAttribute('data-pg')"), J("location.hash")]
            c.tecla('End', 'End', 35); time.sleep(.4); f2 = [sel(), J("document.activeElement&&document.activeElement.getAttribute('data-pg')")]
            c.tecla('Home', 'Home', 36); time.sleep(.4); f3 = [sel(), J("document.activeElement&&document.activeElement.getAttribute('data-pg')"), J("location.hash")]
            chk('P7b seta para a direita troca a aba e leva o foco (Suprimentos, #mod=sup); End vai ao Crédito; Home volta a Prioridades e limpa o endereço',
                f1 == ['sup', 'sup', '#mod=sup'] and f2 == ['cre', 'cre'] and f3 == ['pri', 'pri', ''], [f1, f2, f3])
        for m in ('pri', 'agr', 'man', 'sup', 'com', 'cre'):
            c.goto(U('PG.dc.html' + ('' if m == 'pri' else '#mod=' + m)), 1.0); espera("document.querySelectorAll('[role=tab][data-pg]').length===6"); time.sleep(.3)
            d = json.loads(J(r"""JSON.stringify({sw:document.documentElement.scrollWidth, vw:innerWidth,
              vaza:[...document.querySelectorAll('[role=tabpanel] .pg-card, [role=tabpanel] .pg-it, [role=tabpanel] .pg-bloco')].filter(e=>{const r=e.getBoundingClientRect(); const p=e.closest('main')||document.body; const q=p.getBoundingClientRect(); return r.width>0&&(r.right>q.right+1||r.left<q.left-1);}).length,
              cards:document.querySelectorAll('[role=tabpanel] .pg-card').length, dicas:[...document.querySelectorAll('[role=tabpanel] .pg-card .pg-tip')].filter(b=>(b.getAttribute('data-dica')||'').length>20).length,
              tab44:[...document.querySelectorAll('[role=tab][data-pg]')].every(b=>b.getBoundingClientRect().height>=44),
              alvo44:[...document.querySelectorAll('[role=tabpanel] .pg-it, [role=tabpanel] .pg-cl, [role=tabpanel] .pg-bh a')].filter(e=>e.getBoundingClientRect().height>0).every(e=>e.getBoundingClientRect().height>=44),
              itens:document.querySelectorAll('[role=tabpanel] .pg-it').length, semdados:[...document.querySelectorAll('[role=tabpanel] .pg-v')].filter(e=>e.innerText.trim()==='Sem dados').length})""") or '{}')
            chk(f'P7c {tag} {m}: nada vaza na largura; abas e alvos com 44 px; cada cartão com a dica da conta', d.get('sw', 9e9) <= d.get('vw', 0) and d.get('vaza') == 0 and d.get('tab44') and d.get('alvo44') and d.get('dicas') == d.get('cards'), d)
            if m == 'pri':
                chk(f'P7d {tag}: Prioridades com alavancas, "Atacar agora" e "Decidir"; nenhum indicador "Sem dados" na semente', d.get('itens', 0) >= 7 and d.get('semdados') == 0 and
                    J("[...document.querySelectorAll('[role=tabpanel] section h2')].map(h=>h.innerText.split(' · ')[0]).join('|')") == 'Alavancas do resultado|Atacar agora|Decidir', d)
        # o item leva à origem
        c.goto(U('PG.dc.html'), 1.0); espera("document.querySelectorAll('[role=tabpanel] .pg-it').length>0")
        h1 = J("document.querySelector('[role=tabpanel] .pg-it').getAttribute('href')"); J("document.querySelector('[role=tabpanel] .pg-it').click()")
        espera("!location.pathname.endsWith('PG.dc.html')", 6)
        chk(f'P7e {tag}: o 1º item de "Atacar agora" leva à origem dele ({h1})', bool(h1) and J("location.pathname.split('/').pop()") == h1.split('#')[0], [h1, J("location.pathname")])
        ee = [e for e in (J("window.__errs||[]") or [])]
        chk(f'P7f {tag}: sem erro de JavaScript', not ee, ee[:3])
        if W == 1440:
            c.goto(U('PG.dc.html#mod=com'), 1.0); time.sleep(.4)
            ls1 = J("JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
            chk('P5b navegar pelas abas não grava no armazenamento do navegador', ls0 == ls1, [ls0[:200], ls1[:200]])
            # ---------- P8 Comercial ----------
            c.goto(U('MOD-COM.dc.html'), 1.0)
            cm = J("[...document.querySelectorAll('main a')].map(a=>[a.getAttribute('href'),a.innerText.replace(/\\s+/g,' ').trim()]).filter(x=>/PG\\.dc|PCOM|VEN|EXPED|IV\\./.test(x[0]))")
            c.goto(U('PCOM.dc.html'), 1.0); t = J("(document.querySelector('header h1')||document.querySelector('h1')||{}).innerText||''")
            chk('P8 Comercial: Painel → aba do painel único; "Oferta e compromissos" → PCOM, com o mesmo título', any(x[0] == 'PG.dc.html#mod=com' for x in cm) and any(x[0] == 'PCOM.dc.html' and 'Oferta' in x[1] for x in cm) and t.strip() == 'Oferta e compromissos', [cm, t])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK} ok · {FAIL} falhas')
sys.exit(1 if FAIL else 0)
