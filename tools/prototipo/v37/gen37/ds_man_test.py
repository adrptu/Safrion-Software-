# -*- coding: utf-8 -*-
"""DS-MAN · Manutenção no padrão visual do Agrícola (proprietário, 17/10/2026, 23h: "Design system de manutenção ainda não está no padrão").
Referência: Agrícola › Ordem de Serviço (cabeçalho, bloco "Ordens por fase") e a tela de entrada MOD-AGR. A medição por regra (ds_modulos.py)
dava 0 desvio para a Manutenção; a comparação por captura mostrava os desvios abaixo, que agora são medidos aqui, a 1440 × 900, perfil Ana:
  C  cabeçalho (CAB-3, CAB-4): trilha "Manutenção › <visão>", título da visão (≠ nome do módulo do "‹ Módulo"), selo ao lado, no máximo uma
     primária verde e nenhum texto solto além de título, selo e ações (o motivo de indisponível é o da peça comum engine.acao_motivo)
  A  abas (ABA-01, ABA-02): uma fileira de escolha fora do bloco; o número da aba só aparece maior que zero, com a dica que o explica, e é o
     mesmo da lista aberta ou de um filtro rápido da visão
  B  bloco (BLO-01): a lista dentro de um bloco com título; os filtros rápidos dentro do bloco; Ordens com as fases e no máximo 2 recortes
  L  linhas (TAB-14): célula da tabela com no máximo 2 linhas e cabeçalho de coluna numa linha, a 1440 px
  E  entrada do módulo (MOD-MAN): cartões em blocos com título, como o MOD-AGR; acima deles só a linha de pendência (MA-VINCULO); os mesmos 5 destinos
  R  referência: a O.S. do Agrícola passa nas mesmas medidas C e L (controle do oráculo: a régua é a da tela aprovada)
Contraprova: RENDER_DIR=<render da v129 (5466c6d)> reprova C, A, B, L e E.
Inventário (proteção "nenhuma função some"): --inventario <saida.json> grava, por visão e perfil Otávio, os rótulos de botões, links, itens
de menu (⋯), listas de escolha e links das linhas; compare antes e depois com --compara <antes.json> <depois.json>.
Outros modos: --capturas <pasta> <prefixo> (fotos 1440 × 900 e 390 × 844 das telas da frente) e --todas <saida.json> (as mesmas regras medidas nas
telas do menu de todos os módulos, para a próxima frente; só mede, não reprova).
Uso (de gen37/, depois de build.py + montar_render.py): env CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B ds_man_test.py"""
import os, sys, json, time, re
G = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, G)

R = os.environ.get('RENDER_DIR') or os.path.join(G, '_render')
VISOES = [('semordem', 'vis=semordem'), ('ordens', 'vis=ordens'), ('ativos', 'vis=ativos'), ('abast', 'vis=ativos&modo=abastecimentos'), ('planos', 'vis=planos')]
DETALHES = [('ativo', 'ativo=a01'), ('plano', 'plano=PM-01')]
MODULO = 'Manutenção'

# ---------- medidas (JS) ----------
N = "const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); if(r.width<1||r.height<1) return false; const cs=getComputedStyle(e); return cs.visibility!=='hidden'&&cs.display!=='none'; };"
# linhas de texto de um elemento: os retângulos de cada linha de cada texto (Range.getClientRects), agrupados por sobreposição vertical
LINHAS = ("const linhas=(el)=>{ const rs=[]; const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT); let t;"
          " while((t=w.nextNode())){ if(!t.textContent.trim()) continue; const p=t.parentElement; if(!p||!p.getClientRects().length||p.closest('.g2sr,.ma-sr,svg')) continue;"
          "  const cs=getComputedStyle(p); if(cs.visibility==='hidden'||cs.display==='none') continue; const r=document.createRange(); r.selectNodeContents(t);"
          "  for(const q of r.getClientRects()) if(q.width>.5&&q.height>.5) rs.push([q.top,q.bottom]); }"
          " rs.sort((a,b)=>a[0]-b[0]); let k=0, bot=-1e9; for(const [a,b] of rs){ if(a>=bot-2){ k++; bot=b; } else bot=Math.max(bot,b); } return k; };")

CAB = r"""(()=>{ %s
 const hd=document.querySelector('header'); const h1=hd&&hd.querySelector('h1'); if(!h1) return null; const fila=h1.parentElement;
 const trilha=n((hd.firstElementChild||{}).innerText);
 const volta=hd.querySelector('a.volta37'); const vt=volta?n(volta.innerText).replace(/^‹\s*/,''):'';
 // selo: o 1º elemento depois do título (e do ⓘ) que traz um selo (pílula com fundo)
 let selo=null; for(let e=h1.nextElementSibling;e;e=e.nextElementSibling){ if(e.matches('.g2-info')) continue; if(e.tagName==='SPAN'&&n(e.innerText)){ selo=e; } break; }
 const permitido=(p)=>p.closest('h1,button,a,[role=menu],.g2mais-w,.g2ind')||(selo&&selo.contains(p));
 const soltos=[]; const w=document.createTreeWalker(fila,NodeFilter.SHOW_TEXT); let t;
 while((t=w.nextNode())){ const s=n(t.textContent); if(!s) continue; const p=t.parentElement; if(!vis(p)||p.closest('.g2sr,.ma-sr')) continue; if(!permitido(p)) soltos.push(s.slice(0,60)); }
 const verde=e=>getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)'||/background:\s*(rgb\(30, 122, 76\)|#1E7A4C)/i.test(e.getAttribute('style')||'');
 const prims=[...fila.querySelectorAll('button,a')].filter(b=>vis(b)&&!b.closest('.g2mais-menu')&&verde(b)).map(b=>n(b.innerText));
 const vistos=[...fila.querySelectorAll('button,a')].filter(b=>vis(b)&&!b.closest('.g2mais-menu')&&!b.matches('.g2mais,.volta37,.g2-info')).map(b=>n(b.innerText));
 const ind=[...fila.querySelectorAll('[aria-disabled=true],button:disabled')].filter(vis).map(b=>{ const pr=b.closest('.g2ind'); const mt=pr?pr.querySelector('.g2motivo'):null; return {t:n(b.innerText),dica:b.getAttribute('data-dica')||'',mot:mt&&vis(mt)?n(mt.innerText):''}; });
 return {trilha,h1:n(h1.innerText),volta:vt,selo:selo?n(selo.innerText):'',soltos,prims,vistos,ind}; })()""" % N

ABAS = r"""(()=>{ %s
 const main=document.querySelector('main'); const sec=[...main.querySelectorAll('section')].filter(vis);
 const grupos=[...main.querySelectorAll('[role=group],[role=tablist],[role=radiogroup],[role=toolbar]')].filter(g=>vis(g)&&!g.closest('section,.mf-tela,[role=dialog],aside')&&[...g.querySelectorAll('button[aria-pressed],[role=tab],[role=radio]')].filter(vis).length>=2);
 const tops=[...new Set(grupos.map(g=>Math.round(g.getBoundingClientRect().top/6)))];
 const abas=[...main.querySelectorAll('.ma-vis button,[role=tablist] [role=tab]')].filter(vis).map(b=>{ const m=n(b.innerText).match(/(\d+)\s*$/); return {t:n(b.innerText).replace(/\s*\d+\s*$/,''),n:m?Number(m[1]):null,dica:b.getAttribute('data-dica')||'',lab:b.getAttribute('aria-label')||'',on:b.getAttribute('aria-pressed')==='true'||b.getAttribute('aria-selected')==='true'}; });
 const tab=[...main.querySelectorAll('[role=table][data-g2g]')].find(vis);
 const blocoTab=tab?tab.closest('section'):null; const titulo=blocoTab?n((blocoTab.querySelector('h2,h3')||{}).innerText):'';
 const nlin=tab?[...tab.querySelectorAll('[role=row][data-rid]')].filter(r=>r.getClientRects().length).length:null;
 const chips=[...main.querySelectorAll('button[aria-pressed]')].filter(b=>vis(b)&&!b.closest('.ma-vis,.g2visoes,.mf-tela')).map(b=>({t:n(b.innerText),dentro:!!b.closest('section'),n:(n(b.innerText).match(/(\d+)\s*$/)||[])[1]}));
 return {fileiras:tops.length,grupos:grupos.map(g=>g.getAttribute('aria-label')||g.className),abas,titulo,nlin,chips,secoes:sec.length}; })()""" % N

LINHAS_JS = r"""(()=>{ %s %s
 const out={celulas:[],cab:[],tabelas:[]};
 [...document.querySelectorAll('main [role=table][data-g2g]')].filter(vis).forEach(t=>{ const gid=t.getAttribute('data-g2g'); out.tabelas.push(gid);
   const hs=[...t.querySelectorAll('[role=columnheader]')]; const rot=hs.map(h=>n(h.innerText));
   hs.forEach((h,i)=>{ const l=h.querySelector('.g2hl')||h; const k=linhas(l); if(k>1) out.cab.push({gid,col:rot[i],linhas:k}); });
   [...t.querySelectorAll('[role=row][data-rid]')].filter(r=>r.getClientRects().length).forEach(r=>{ [...r.querySelectorAll(':scope>[role=cell]')].forEach((c,i)=>{ const k=linhas(c); if(k>2) out.celulas.push({gid,rid:r.getAttribute('data-rid'),col:rot[i]||String(i),linhas:k,t:n(c.innerText).slice(0,70)}); }); }); });
 return out; })()""" % (N, LINHAS)

ENTRADA = r"""(()=>{ %s
 const main=document.querySelector('main'); const blocos=[...main.querySelectorAll('section')].filter(vis).map(s=>({t:n((s.querySelector('h2,h3')||{}).innerText),cartoes:[...s.querySelectorAll('a.mod-cartao')].map(a=>[n(a.innerText),a.getAttribute('href')])}));
 const cartoes=[...main.querySelectorAll('a.mod-cartao')].filter(vis).map(a=>[n(a.innerText),a.getAttribute('href')]);
 const primeiro=main.querySelector('a.mod-cartao'); const acima=[...main.querySelectorAll('a,[role=note],[role=alert]')].filter(e=>vis(e)&&!e.matches('a.mod-cartao')&&primeiro&&(e.compareDocumentPosition(primeiro)&Node.DOCUMENT_POSITION_FOLLOWING)).map(e=>n(e.innerText).slice(0,60));
 return {blocos,cartoes,acima}; })()""" % N

INV = r"""(()=>{ %s const norm=t=>n(t).replace(/\d+([.,]\d+)*/g,'#');
 const out={cabecalho:[],menu_cabecalho:[],tela:[],menus:[],listas:[],linhas:[]};
 const hd=document.querySelector('header'); const m=document.querySelector('main');
 hd.querySelectorAll('button,a[href]').forEach(b=>{ if(b.closest('nav')) return; const t=norm(b.innerText||b.getAttribute('aria-label')); if(!t) return; if(b.closest('.g2mais-menu')) out.menu_cabecalho.push(t); else if(vis(b)) out.cabecalho.push(t); });
 m.querySelectorAll('button,a[href]').forEach(b=>{ const t=norm(b.innerText||b.getAttribute('aria-label')); if(!t) return; const lin=b.closest('[role=row][data-rid],.g2cd');
   if(lin){ if(b.closest('.g2mais-menu')) out.linhas.push('⋯ '+t); else if(vis(b)) out.linhas.push(t); return; }
   if(b.closest('.g2mais-menu')) out.menus.push(t); else if(vis(b)) out.tela.push(t); });
 m.querySelectorAll('select').forEach(s=>{ if(vis(s)) out.listas.push(n(s.getAttribute('aria-label'))+': '+[...s.options].map(o=>n(o.text)).join(' | ')); });
 for(const k in out) out[k]=[...new Set(out[k])].sort(); return out; })()""" % N


def main():
    from comp_lib import Chrome, servir
    p, srv = servir(R); c = Chrome(); J = c.js; U = f'http://127.0.0.1:{p}/'
    OK, FAIL = [], []
    def chk(nome, cond, extra=''):
        (OK if cond else FAIL).append(nome); print(('  ok  ' if cond else '  FALHA ') + nome + ('' if cond else ' · ' + json.dumps(extra, ensure_ascii=False)[:600]), flush=True)
    def ir(pg, hash_='', espera=1.4, perfil='Ana'):
        c.goto(U + 'Main.dc.html', .3); J(f"localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")
        c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.15); c.goto(U + pg + (('#' + hash_) if hash_ else ''), espera)
    inv = '--inventario' in sys.argv
    try:
        if '--capturas' in sys.argv:   # fotos das telas da frente: <pasta> <prefixo> (antes|depois), 1440 × 900 e 390 × 844 (toque)
            i = sys.argv.index('--capturas'); pasta, pre = sys.argv[i + 1], sys.argv[i + 2]; os.makedirs(pasta, exist_ok=True)
            telas = [('MOD-MAN', 'MOD-MAN.dc.html', '', 'Ana')] + [(f'MA-{k}', 'MA.dc.html', h, 'Ana') for k, h in VISOES] + [('PG-man', 'PG.dc.html', 'mod=man', 'Ana')]   # PAINEL-03 (18/10): o Painel da Manutenção é a aba do painel único
            for w, h_, toque in ((1440, 900, False), (390, 844, True)):
                c.aparelho(w, h_, 1, toque)
                for nome, pg, h, perfil in telas + ([(f'MA-{k}-otavio', 'MA.dc.html', hh, 'Otávio') for k, hh in VISOES[:1] + VISOES[2:3]] + [(f'MA-{k}', 'MA.dc.html', hh, 'Ana') for k, hh in DETALHES] if w == 1440 else []):
                    ir(pg, h, espera=1.8, perfil=perfil); J("document.querySelectorAll('aside[role=dialog] button[aria-label^=Fechar]').forEach(b=>b.click())"); time.sleep(.4)
                    c.shot(os.path.join(pasta, f'{pre}_{nome}_{w}.png'))
            print('capturas em', pasta); return 0
        if '--todas' in sys.argv:   # inventário das mesmas regras nas telas do menu de todos os módulos (só mede; não reprova): <saida.json>
            import glob, ui37
            saida = sys.argv[sys.argv.index('--todas') + 1]; c.aparelho(1440, 900, 1, False); res = {}
            pags = sorted({h.split('#')[0] for _n, _i, its in ui37.MENU2 for _l, h in its} | set(ui37.HUB37.values()))
            for pg in pags:
                if not os.path.exists(os.path.join(R, pg)): continue
                ir(pg); cab = J(CAB) or {}; ab = J(ABAS) or {}; lin = J(LINHAS_JS) or {}; mod = next((n for n, _i, its in ui37.MENU2 if any(h.split('#')[0] == pg for _l, h in its) or ui37.HUB37.get(n) == pg), '')
                res[pg] = dict(modulo=mod, h1=cab.get('h1'), volta=cab.get('volta'), soltos=cab.get('soltos'), fileiras=ab.get('fileiras'), bloco=ab.get('titulo'),
                               celulas3=len(lin.get('celulas') or []), cab2=len(lin.get('cab') or []), ex=(lin.get('celulas') or [])[:2])
                d = res[pg]; print(f"{pg:22} {mod:14} CAB-3 {'x' if d['h1'] and d['h1'] == d['volta'] else '.'} CAB-4 {len(d['soltos'] or [])} ABA-01 {d['fileiras']} TAB-14 {d['celulas3']} cab {d['cab2']}", flush=True)
            json.dump(res, open(saida, 'w'), ensure_ascii=False, indent=1); print('inventário de todas as telas do menu:', saida); return 0
        c.aparelho(1440, 900, 1, False)
        if inv:
            saida = sys.argv[sys.argv.index('--inventario') + 1]; res = {}
            for nome, h in VISOES + DETALHES:
                ir('MA.dc.html', h, perfil='Otávio'); J("document.querySelectorAll('aside[role=dialog] button[aria-label^=Fechar]').forEach(b=>b.click())"); time.sleep(.3)
                res[nome] = J(INV)
            for pg in ('MOD-MAN.dc.html', 'PG.dc.html'):   # PAINEL-03: o Painel da Manutenção é a aba do painel único
                ir(pg, 'mod=man' if pg == 'PG.dc.html' else '', perfil='Otávio'); res[pg] = J(INV)
            json.dump(res, open(saida, 'w'), ensure_ascii=False, indent=1); print('inventário:', saida); return 0
        # ---------- R · referência (O.S.): a régua mede o que a tela aprovada cumpre ----------
        ir('OS.dc.html'); cab = J(CAB); lin = J(LINHAS_JS)
        chk('R1 referência O.S.: trilha "Agrícola › Ordem de Serviço", título ≠ módulo, sem texto solto, uma primária', cab and cab['trilha'] == 'Agrícola › Ordem de Serviço' and cab['h1'] != cab['volta'] and not cab['soltos'] and len(cab['prims']) == 1, cab)
        chk('R2 referência O.S.: células com até 2 linhas e cabeçalho numa linha a 1440 px', lin and not lin['celulas'] and not lin['cab'] and lin['tabelas'], lin)
        # ---------- C, A, B, L · as visões da Manutenção ----------
        nomes = {}
        for nome, h in VISOES + DETALHES:
            ir('MA.dc.html', h); cab = J(CAB) or {}; nomes[nome] = cab.get('h1', '')
            det = nome in ('ativo', 'plano')
            chk(f'C1 {nome}: título da visão ({cab.get("h1")!r}) ≠ nome do módulo do "‹ {MODULO}"', cab.get('h1') and cab.get('h1') != cab.get('volta') and cab.get('volta') == MODULO, cab)
            chk(f'C2 {nome}: trilha "{MODULO} › {cab.get("h1")}"' + (' › registro' if det else ''), cab.get('trilha', '').startswith(f'{MODULO} › {cab.get("h1")}') and (det or cab.get('trilha') == f'{MODULO} › {cab.get("h1")}'), cab.get('trilha'))
            chk(f'C3 {nome}: nenhum texto solto no cabeçalho além de título, selo e ações', not cab.get('soltos'), cab.get('soltos'))
            chk(f'C4 {nome}: no máximo uma primária verde à vista e selo de estado ao lado do título', len(cab.get('prims') or []) <= 1 and len(cab.get('vistos') or []) <= 1 and bool(cab.get('selo')), [cab.get('prims'), cab.get('vistos'), cab.get('selo')])
            ind = cab.get('ind') or []
            chk(f'C5 {nome}: ação indisponível com o motivo na dica e junto do botão (peça comum acao_motivo)', all(x['dica'] and x['mot'] == x['dica'] for x in ind), ind)
            if det: continue
            ab = J(ABAS) or {}
            chk(f'A1 {nome}: uma fileira de escolha fora do bloco (as abas das visões)', ab.get('fileiras') == 1, [ab.get('fileiras'), ab.get('grupos')])
            chk(f'B1 {nome}: a lista dentro de um bloco com título ({ab.get("titulo")!r})', bool(ab.get('titulo')), ab.get('titulo'))
            fora = [x['t'] for x in ab.get('chips') or [] if not x['dentro']]
            chk(f'B2 {nome}: filtros rápidos dentro do bloco', not fora, fora)
            if nome == 'ordens':
                rec = [x['t'] for x in ab.get('chips') or [] if x['dentro'] and not re.match(r'^(Todas|A liberar|Liberadas|Em execução|Em conferência|Encerradas)\b', x['t'])]
                chk('B3 ordens: fases + no máximo 2 recortes de ação no bloco', len(rec) <= 2, rec)
            lin = J(LINHAS_JS) or {}
            chk(f'L1 {nome}: células com no máximo 2 linhas a 1440 px', lin.get('tabelas') and not lin.get('celulas'), lin.get('celulas', [])[:6])
            chk(f'L2 {nome}: cabeçalhos de coluna numa linha', lin.get('tabelas') and not lin.get('cab'), lin.get('cab'))
        chk('C6 títulos diferentes por visão (o título diz a tela)', len({nomes[k] for k, _ in VISOES if k != 'abast'}) == 4, nomes)
        # C7 · indisponível de verdade: Ana (sem o papel) toca "Criar plano" e "Vincular a plano"; nada abre, a dica diz o porquê
        for h, rot, pan in (('vis=planos', 'Criar plano', '#np-painel'), ('vis=ativos', 'Vincular a plano', '#vl-painel')):
            ir('MA.dc.html', h)
            r = J(f"(()=>{{const b=[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==={json.dumps(rot)}); if(!b) return null; b.click();"
                  f" return new Promise(ok=>setTimeout(()=>ok({{painel:!!document.querySelector({json.dumps(pan)}),dica:((document.getElementById('g2-dica')||{{}}).innerText||'').trim()}}),400)); }})()")
            chk(f'C7 Ana · "{rot}" indisponível: o toque não abre o painel e a dica diz o motivo', r and not r['painel'] and 'Otávio' in r['dica'], r)
        # ---------- L3, L4 · as mesmas medidas com todas as colunas à vista (a escolha "Colunas" da pessoa) ----------
        from comp_lib import cv_todas_sempre, cv_padrao
        cv_todas_sempre(c)
        try:
            for larg in (1440, 1280):   # 1280 × 800: a grade inteira cabe sem rolagem lateral escondida (ma_correcoes_om_test 8)
                c.aparelho(larg, 900 if larg == 1440 else 800, 1, False)
                for nome, h in VISOES:
                    ir('MA.dc.html', h); lin = J(LINHAS_JS) or {}
                    lado = J("(()=>{const r=[...document.querySelectorAll('main .g2rola')].find(e=>e.getClientRects().length); return r?r.scrollWidth-r.clientWidth:null;})()")
                    chk(f'L3 {nome} (todas as colunas, {larg} px): células com no máximo 2 linhas e sem rolagem lateral', lin.get('tabelas') and not lin.get('celulas') and (lado or 0) <= 1, [lado, lin.get('celulas', [])[:6]])
                    chk(f'L4 {nome} (todas as colunas, {larg} px): cabeçalhos de coluna numa linha', lin.get('tabelas') and not lin.get('cab'), lin.get('cab'))
        finally:
            cv_padrao(c); c.aparelho(1440, 900, 1, False)
        # ---------- A2 · número da aba = o da lista aberta ou do filtro rápido que ele conta; só > 0 e com dica ----------
        # o filtro rápido de cada aba (o mesmo sentido da dica): Sem ordem = a lista aberta (até 10 d); Ordens = Aguardam você; Ativos = Bloqueado
        FONTE = {'Sem ordem': 'Até 10 d', 'Ordens': 'Aguardam você', 'Ativos': 'Bloqueado'}
        for perfil in ('Ana', 'Otávio', 'Zé'):
            ir('MA.dc.html', 'vis=semordem', perfil=perfil); abas = (J(ABAS) or {}).get('abas') or []
            for a in abas:
                k = {'Sem ordem': 'vis=semordem', 'Ordens': 'vis=ordens', 'Ativos': 'vis=ativos', 'Planos': 'vis=planos'}.get(a['t'])
                if a['n'] is None or not k: continue
                ir('MA.dc.html', k, perfil=perfil); J("document.querySelectorAll('aside[role=dialog] button[aria-label^=Fechar]').forEach(b=>b.click())"); time.sleep(.3)
                v = J(ABAS) or {}; fonte = FONTE.get(a['t'], '')
                nums = [int(x['n']) for x in v.get('chips') or [] if x.get('dentro') and x.get('n') and re.sub(r'\s*\d+\s*$', '', x['t']) == fonte]
                chk(f'A2 {perfil} · {a["t"]} {a["n"]}: número > 0, com dica, igual à lista aberta ({v.get("nlin")}) ou ao filtro rápido "{fonte}" {nums}',
                    a['n'] > 0 and str(a['n']) in a['dica'] and (a['n'] == v.get('nlin') or a['n'] in nums), [a, v.get('nlin'), nums])
        # ---------- E · entrada do módulo ----------
        ir('MOD-MAN.dc.html'); e = J(ENTRADA) or {}
        dest = sorted(h for _, h in e.get('cartoes') or [])
        chk('E1 MOD-MAN: cartões em blocos com título (como o MOD-AGR)', len(e.get('blocos') or []) >= 2 and all(b['t'] and b['cartoes'] for b in e['blocos']), e.get('blocos'))
        # ENT-01 (revisão do integrador, 18/10/2026): acima dos blocos só a linha de pendência do MA-VINCULO (um toque para a lista filtrada)
        ac = e.get('acima') or []
        chk('E2 MOD-MAN: acima dos cartões, só a linha de pendência "N ativos sem plano · Vincular ›" (um toque) e nada mais',
            len(ac) <= 1 and all(x.endswith('Vincular ›') and 'sem plano' in x for x in ac), ac)
        chk('E3 MOD-MAN: os mesmos 5 destinos (Painel e as 4 visões)', dest == sorted(['PG.dc.html#mod=man', 'MA.dc.html#vis=semordem', 'MA.dc.html#vis=ordens', 'MA.dc.html#vis=ativos', 'MA.dc.html#vis=planos']), dest)
        ir('MOD-AGR.dc.html'); ea = J(ENTRADA) or {}
        chk('E4 referência MOD-AGR: blocos com título e sem aviso solto (a régua é a da tela aprovada)', len(ea.get('blocos') or []) >= 2 and not ea.get('acima'), ea.get('blocos'))
        erros = J("window.__errs||[]") or []
        chk('Z sem erro de JS', not erros, erros[:3])
    finally:
        c.close(); srv.terminate()
    print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
    return 1 if FAIL else 0


def compara(a, b):
    """o que estava à vista ou no ⋯ antes e não está depois (por visão); o que mudou de lugar aparece nos dois lados"""
    A, B = json.load(open(a)), json.load(open(b)); sai = {}
    for vis, x in A.items():
        y = B.get(vis, {}); tudo_b = {t for k in y for t in y[k]}
        perd = {k: [t for t in x[k] if t not in tudo_b] for k in x}
        perd = {k: v for k, v in perd.items() if v}
        if perd: sai[vis] = perd
    return sai


if __name__ == '__main__':
    if '--compara' in sys.argv:
        i = sys.argv.index('--compara'); print(json.dumps(compara(sys.argv[i + 1], sys.argv[i + 2]), ensure_ascii=False, indent=1)); sys.exit(0)
    sys.exit(main())
