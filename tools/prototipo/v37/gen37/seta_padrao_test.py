# -*- coding: utf-8 -*-
"""TAB-11 · Seta única de abrir e de ir (proprietário, 16/10/2026, com a captura do CD-01: "mude o estilo do drill down daquele preto para a
setinha mais intuitiva e amigável dos debaixo, melhore ela e implemente como nosso padrão em tudo"; docs/design-system/padroes-1610.md).
Varre todas as páginas do _render (fora Main e os redirecionamentos) e os estados que só abrem por endereço ou por um clique (painéis da
Manutenção e da O.S., Atividades do plano, Capacidade por mês, ajuste local do Planejar safra, laudo de solo, Registrar laudo, Kanban agrupado,
barra do lote do CA-01 com uma linha escolhida), a 1440 × 900 e a 390 × 844
(toque), no estado inicial, com "Expandir tudo" e no outro modo de Tabela | Cartões:
  A  nenhum triângulo de abrir (▸ ▾ ▹ ▿ ▶ ►; ▼ em controle de abrir) como texto em botão, link, summary ou [aria-expanded], nem no começo
     de linha; lista suspensa (aria-haspopup), ordenação do cabeçalho e menus ficam fora (o ▾ da lista suspensa continua no fim, TAB-09);
  B  todo controle de abrir/recolher (aria-expanded ou summary; fora lista suspensa, menu ⋯ e campo) tem o componente .g2seta como filho
     direto, ou é o nome visível de uma linha cuja seta (.g2car) controla a mesma região (aria-controls);
  C  a seta é uma só: cor computada (texto secundário #65736A), 16 × 16 px, traço de 1,75 e o mesmo desenho em todas as telas;
  D  o giro segue o estado: aria-expanded=true (ou details aberto) → rotate(90°); fechado → sem giro (a seta de ir, .g2drill, saiu: TAB-13);
  E  teclado: Enter e Espaço na seta alternam o aria-expanded sem abrir painel; o foco é visível (anel de 2 px verde) — uma seta por tela;
  F  alvo: botão da seta ≥ 44 × 44 px a 390 (toque) e ≥ 24 × 24 px a 1440, sem cobrir outro controle da linha; botão com o nome à vista
     (seção, lote, summary) ≥ 44 px de altura a 390;
  G  sem erro de JavaScript.
Contraprova: RENDER_DIR=<render da base c9ffa08> reprova A e B (triângulo preto de texto, sem o componente).
Uso (de gen37/): CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B seta_padrao_test.py · SPT_LARG=1440 ou 390 (padrão: as duas)
· SPT_SO=CD-01,PA (diagnóstico de poucas telas; os limites mínimos de contagem fazem a rodada parcial reprovar: não vale como prova)
Saída: uma linha por desvio (até 30 por regra) e o RESULTADO; sai 1 se falhar."""
import os, sys, json, glob, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from areas.maquinas import REDIRECIONA

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
LARGS = [int(x) for x in (os.environ.get('SPT_LARG') or '1440,390').split(',')]
FORA = set(REDIRECIONA) | {'Main.dc.html'}
PAGS = sorted(os.path.basename(f) for f in glob.glob(os.path.join(R, '*.dc.html')) if os.path.basename(f) not in FORA)
# estados que só abrem por endereço (painel aberto, plano aberto, visão) ou por um clique (ajuste local do Planejar safra)
EXTRAS = ['PA.dc.html#plano=SOJA-AT', 'PA.dc.html?view=tabela#plano=SOJA-AT', 'SAF.dc.html#saf=S2627&passo=operacoes',
          'MA.dc.html#ativo=a01', 'MA.dc.html#om=OM-0233', 'MA.dc.html#plano=PM-01', 'OS.dc.html#OS-0420', 'OS.dc.html?view=kanban&ag=onde', 'AG-02.dc.html#LAU-2073',
          'SAF.dc.html#saf=S2627&passo=cultivos|ajuste', 'AG-02.dc.html#registrar=Santa%20Rita%2FT3', 'CA-01.dc.html|sel1']
SO = [x for x in (os.environ.get('SPT_SO') or '').split(',') if x]   # diagnóstico: só as telas cujo endereço contém um destes trechos (não vale como rodada)
if SO: PAGS, EXTRAS = [p for p in PAGS if any(x in p for x in SO)], [p for p in EXTRAS if any(x in p for x in SO)]
COR, TAM, TRACO = 'rgb(101, 115, 106)', 16, '1.75'
OK, FAIL = [], []
# mínimos da rodada completa (contagem de controles e de setas desenhadas, somando os estados): desde 17/10 a abertura é recolhida (TAB-12:
# os filhos e as setas deles só aparecem com "Expandir tudo") e a seta de ir saiu das linhas folha (TAB-13), então há menos setas à vista;
# antes eram 300 controles e 500 setas (1.340 delas de ir, na composição bde9f57)
MIN_CTL, MIN_ICO = 150, 150
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:1500]), flush=True)

MEDE = r"""((w)=>{
 const vis=e=>{ if(!e||!e.getBoundingClientRect) return false; const r=e.getBoundingClientRect(); if(r.width<=1||r.height<=1) return false; const cs=getComputedStyle(e); return cs.visibility!=='hidden'&&cs.display!=='none'&&parseFloat(cs.opacity)>0.05; };
 const N=s=>(s||'').replace(/\s+/g,' ').trim();
 const nome=e=>e.tagName.toLowerCase()+(e.className&&typeof e.className==='string'&&e.className.trim()?'.'+e.className.trim().split(/\s+/).slice(0,2).join('.'):'');
 const txt=e=>N(e.innerText||e.getAttribute('aria-label')||'').slice(0,44);
 const FORA='[aria-haspopup],[role=combobox],[role=columnheader],[role=menu],[role=listbox],.g2dsel';
 const out={a:[],b:[],c:{},d:[],f:[],nCtl:0,nIco:0,nDrill:0};
 // A · triângulo de abrir como texto
 const GA=/[▸▾▹▿▶►]/, GB=/▼/;
 for(const e of [...document.querySelectorAll('button,a[href],[role=button],summary,[aria-expanded]')].filter(vis)){
   if(e.closest(FORA)) continue; const t=e.innerText||'';
   const abre=e.hasAttribute('aria-expanded')||e.tagName==='SUMMARY'||e.classList.contains('g2car');
   if(GA.test(t)||(abre&&GB.test(t))) out.a.push(nome(e)+' «'+N(t).slice(0,40)+'»'); }
 for(const r of [...document.querySelectorAll('[role=row],[role=listitem]')].filter(vis)){ if(/^[▸▾▹▿▶►]/.test(N(r.innerText))) out.a.push('linha «'+N(r.innerText).slice(0,40)+'»'); }
 // B · componente em todo controle de abrir/recolher
 const filho=(e)=>[...e.children].find(x=>x.classList&&x.classList.contains('g2seta'))||e.querySelector(':scope>sc-if>.g2seta,:scope>sc-for>.g2seta');
 const disc=[...document.querySelectorAll('[aria-expanded],summary')].filter(vis).filter(e=>!e.matches('[aria-haspopup],[role=combobox],input,select,textarea,.g2mais,.g2vmais')&&!e.closest('[role=menu],.g2dsel,details.acoes-mais'));
 for(const e of disc){ out.nCtl++; if(filho(e)) continue;
   const ctl=e.getAttribute('aria-controls'); const par=ctl&&[...document.querySelectorAll('.g2car[aria-controls]')].find(b=>b!==e&&b.getAttribute('aria-controls')===ctl&&filho(b));
   if(!par) out.b.push(nome(e)+' «'+txt(e)+'»'); }
 // C · uma seta só (estilo computado) e D · giro coerente com o estado
 for(const s of [...document.querySelectorAll('.g2seta')].filter(vis)){ out.nIco++; const sv=s.querySelector('svg'); if(!sv) { out.d.push('sem svg: '+nome(s.parentElement)); continue; }
   const r=sv.getBoundingClientRect(), p=sv.querySelector('path'); const k=[getComputedStyle(s).color, Math.round(r.width*10)/10+'x'+Math.round(r.height*10)/10, sv.getAttribute('stroke-width'), p?p.getAttribute('d'):'', sv.getAttribute('viewBox')].join(' | ');
   (out.c[k]||(out.c[k]=[])).push(txt(s.closest('button,summary,[role=row],[role=listitem],a')||s.parentElement));
   if(s.classList.contains('g2drill')) out.nDrill++;
   const dono=s.parentElement&&(s.parentElement.matches('sc-if,sc-for')?s.parentElement.parentElement:s.parentElement);
   let quer=false;
   if(s.classList.contains('g2seta-on')) quer=true;
   else if(dono&&dono.hasAttribute('aria-expanded')) quer=dono.getAttribute('aria-expanded')==='true';
   else if(dono&&dono.tagName==='SUMMARY') quer=!!(dono.parentElement&&dono.parentElement.open);
   const tf=getComputedStyle(sv).transform; let ang=0; if(tf&&tf!=='none'){ const m=new DOMMatrix(tf); ang=Math.round(Math.atan2(m.b,m.a)*180/Math.PI); }
   if(quer!==(ang===90)||(ang!==0&&ang!==90)) out.d.push(nome(dono||s)+' «'+txt(dono||s)+'» aria-expanded='+(dono&&dono.getAttribute('aria-expanded'))+' transform='+tf); }
 // F · alvo de toque/clique
 const min=w<=500?44:24;
 for(const b of [...document.querySelectorAll('button.g2car')].filter(vis)){ const r=b.getBoundingClientRect();
   if(r.width<min-0.5||r.height<min-0.5) out.f.push('seta '+Math.round(r.width)+'×'+Math.round(r.height)+' «'+txt(b)+'»');
   const row=b.closest('[role=row],[role=listitem],.pa-atividade-linha,.pm-sv-linha')||b.parentElement;
   for(const o of [...row.querySelectorAll('button,a[href],input,select')].filter(x=>x!==b&&!b.contains(x)&&!x.contains(b)&&vis(x))){ const q=o.getBoundingClientRect();
     const ix=Math.min(r.right,q.right)-Math.max(r.left,q.left), iy=Math.min(r.bottom,q.bottom)-Math.max(r.top,q.top); if(ix>0.5&&iy>0.5){ out.f.push('seta cobre '+nome(o)+' «'+txt(b)+'»'); break; } } }
 if(w<=500) for(const b of disc.filter(e=>filho(e)&&!e.classList.contains('g2car'))){ const r=b.getBoundingClientRect(); if(r.height<43.5) out.f.push('nome+seta '+Math.round(r.height)+' px «'+txt(b)+'»'); }
 return out; })"""

ESTADOS = r"""((k)=>{ const vis=e=>!!e&&e.getClientRects().length>0;
 if(k==='expandir'){ const bs=[...document.querySelectorAll('.g2xtog')].filter(b=>vis(b)&&/Expandir/.test(b.innerText)); bs.forEach(b=>b.click()); return bs.length; }
 if(k==='modo'){ const bs=[...document.querySelectorAll('[data-g2md]')].filter(vis).map(g=>g.querySelector('[data-modo][aria-pressed=false]')).filter(Boolean); bs.forEach(b=>b.click()); return bs.length; }
 return 0; })"""
# ajuste local do Planejar safra: faixa da fazenda → linha do cultivo → painel → "Ajustar insumos e doses de …" (o painel tem grupos e atividades que abrem)
AJUSTE = r"""(async ()=>{ const vis=e=>!!e&&e.getClientRects().length>0, N=s=>(s||'').replace(/\s+/g,' ').trim(), espera=ms=>new Promise(r=>setTimeout(r,ms));
 for(let i=0;i<4;i++){ const f=[...document.querySelectorAll('[role=row].g2fgrp button.g2car[aria-expanded=false]')].find(vis); if(!f) break; f.click(); await espera(400); }   // TAB-12 (17/10): a faixa da fazenda nasce recolhida; a pessoa a abre
 for(const t of ['T7','T3','T2','T4','T5','T6']){ const row=[...document.querySelectorAll('[role=row].g2ed')].filter(vis).find(r=>new RegExp('^'+t+'\\b').test(N(r.innerText))); if(!row) continue;
   (row.querySelector('.g2pw')||row).click(); await espera(500);
   const b=[...document.querySelectorAll('aside[role=dialog] button')].filter(vis).find(x=>/^(Ajustar|Ver) insumos e doses de /.test(N(x.innerText))); if(b){ b.click(); await espera(600); return 'ok'; } }
 return 'sem ação de insumos em T7, T3, T2, T4, T5, T6'; })()"""
# seleção de uma linha (a barra do lote mostra o que só aparece com seleção, ex.: "Conferir caminho de liberação" do CA-01)
SEL1 = r"""(async ()=>{ const vis=e=>!!e&&e.getClientRects().length>0; const b=[...document.querySelectorAll('[role=row] input[type=checkbox]')].find(vis);
 if(!b) return 'sem caixa de seleção'; b.click(); await new Promise(r=>setTimeout(r,500)); return 'ok'; })()"""
# E · teclado: Enter e Espaço na 1ª seta visível alternam o aria-expanded, sem abrir painel; o foco fica visível
# o foco chega pelo teclado, como a pessoa: foco na seta, Tab e Shift+Tab de volta (o :focus-visible é o do teclado)
TECLA_ACHA = r"""(()=>{ const vis=e=>{ const r=e.getBoundingClientRect(); return r.width>1&&r.height>1&&r.top>=0&&r.bottom<=innerHeight; };
 const dlg=[...document.querySelectorAll('aside[role=dialog]')].filter(e=>e.getClientRects().length).pop();   // painel aberto: a seta dele (o foco fica preso no painel)
 const b=[...(dlg||document).querySelectorAll('button.g2car[aria-expanded]')].find(vis); if(!b) return false; window.__spB=b; b.focus(); return true; })()"""
TECLA_PREP = r"""(()=>{ const b=window.__spB; if(!b) return null; const cs=getComputedStyle(b);
 return {exp:b.getAttribute('aria-expanded'), fv:document.activeElement===b&&b.matches(':focus-visible'), ow:cs.outlineWidth, os:cs.outlineStyle, oc:cs.outlineColor, lab:b.getAttribute('aria-label')||''}; })()"""
TECLA_LE = r"""(()=>{ const b=window.__spB; if(!b||!b.isConnected){ const n=[...document.querySelectorAll('button.g2car[aria-expanded]')].find(x=>x.getAttribute('aria-label')&&x===document.activeElement); return n?{exp:n.getAttribute('aria-expanded'),foco:true,dlg:document.querySelectorAll('aside[role=dialog]').length}:{exp:null,foco:false,dlg:document.querySelectorAll('aside[role=dialog]').length}; }
 return {exp:b.getAttribute('aria-expanded'), foco:document.activeElement===b, dlg:document.querySelectorAll('aside[role=dialog]').length}; })()"""

# espera as transições em curso terminarem (no máximo 2 s): condição observável, não espera fixa
ANIM = "Promise.race([Promise.all(document.getAnimations().map(a=>a.finished.catch(()=>0))), new Promise(r=>setTimeout(r,2000))]).then(()=>true)"
def varre(c, J, BASE, w):
    res = {'a': [], 'b': [], 'd': [], 'f': [], 'e': [], 'err': []}; estilos = {}; telas = {k: set() for k in res}
    n = {'ctl': 0, 'ico': 0, 'drill': 0, 'tecla': 0}
    for pg in PAGS + EXTRAS:
        url, acao = (pg.split('|') + [''])[:2]
        c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.1); c.goto(BASE + url, 1.0)
        if acao in ('ajuste', 'sel1'):
            r = J(AJUSTE if acao == 'ajuste' else SEL1)
            if r != 'ok': res['err'].append((w, pg, acao + ': ' + str(r)))
        for est in ('inicial', 'expandir', 'modo'):
            if est != 'inicial':
                if acao or not J(f"{ESTADOS}('{est}')"): continue
                time.sleep(.7)
            J(ANIM)   # o giro (120 ms) termina antes de medir: com a abertura recolhida (TAB-12) a seta gira no clique, e a máquina carregada atrasa a transição
            m = J(f"{MEDE}({w})") or {}
            n['ctl'] += m.get('nCtl', 0); n['ico'] += m.get('nIco', 0); n['drill'] += m.get('nDrill', 0)
            for k in ('a', 'b', 'd', 'f'):
                for x in m.get(k) or []: res[k].append((w, pg, est, x)); telas[k].add(pg)
            for k, v in (m.get('c') or {}).items(): estilos.setdefault(k, set()).add(pg)
            if est == 'inicial':   # E · teclado, na 1ª seta visível do estado inicial (Enter e Espaço: volta ao estado de antes)
                p0 = None
                if J(TECLA_ACHA):
                    c.tab(); c.tab(shift=True); time.sleep(.1); p0 = J(TECLA_PREP)
                if p0:
                    n['tecla'] += 1; d0 = J("document.querySelectorAll('aside[role=dialog]').length")
                    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.35); p1 = J(TECLA_LE) or {}
                    c.tecla(' ', 'Space', 32, text=' '); time.sleep(.35); p2 = J(TECLA_LE) or {}
                    anel = p0['fv'] and p0['os'] != 'none' and float(p0['ow'].replace('px', '') or 0) >= 2 and p0['oc'] == 'rgb(30, 122, 76)'
                    if not (anel and p1.get('exp') not in (None, p0['exp']) and p2.get('exp') == p0['exp'] and p1.get('dlg') == d0 and p2.get('dlg') == d0):
                        res['e'].append((w, pg, p0.get('lab', '')[:40], json.dumps(p0, ensure_ascii=False), json.dumps(p1), json.dumps(p2))); telas['e'].add(pg)
                    J("document.activeElement&&document.activeElement.blur&&document.activeElement.blur()")
        for e in (J("window.__errs||[]") or [])[:2]: res['err'].append((w, pg, str(e)[:160]))
        J("try{localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')}catch(e){}")
    return res, estilos, telas, n

p, srv = servir(R); c = Chrome(); J = c.js; BASE = f'http://127.0.0.1:{p}/'
try:
    for w in LARGS:
        h, e, t = (900, 1, False) if w > 500 else (844, 2, True)
        c.aparelho(w, h, e, t); c.goto(BASE + 'Main.dc.html', .3); J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
        res, estilos, telas, n = varre(c, J, BASE, w)
        dd = lambda L: list(dict.fromkeys(L))
        print(f'# {w} px · {len(PAGS)} telas + {len(EXTRAS)} estados · {n["ctl"]} controles de abrir/recolher · {n["ico"]} setas desenhadas ({n["drill"]} de ir) · {n["tecla"]} telas com teclado medido', flush=True)
        print(f'# {w} px · desenhos distintos da seta: {len(estilos)}', flush=True)
        for k, v in sorted(estilos.items(), key=lambda kv: -len(kv[1])): print(f'    {len(v):4d} telas · {k}', flush=True)
        for k in ('a', 'b', 'd', 'f', 'e'):
            for x in dd(res[k])[:30]: print(f'  {k} ', x, flush=True)
        chk(f'A{w} nenhum triângulo de abrir como texto em botão, link, summary, [aria-expanded] ou começo de linha (telas com desvio: {len(telas["a"])})', not res['a'], sorted(telas['a']))
        chk(f'B{w} todo controle de abrir/recolher usa o componente da seta ({n["ctl"]} controles; telas com desvio: {len(telas["b"])})', n['ctl'] > MIN_CTL and not res['b'], sorted(telas['b']))
        so = list(estilos)
        ok_c = len(so) == 1 and so[0].startswith(f'{COR} | {TAM}x{TAM} | {TRACO} | ')
        chk(f'C{w} uma seta só: {COR}, {TAM}×{TAM} px, traço {TRACO}, o mesmo desenho ({n["ico"]} setas; desenhos distintos: {len(so)})', n['ico'] > MIN_ICO and ok_c, so[:4])
        chk(f'D{w} giro coerente com o estado (aberta → 90°, fechada e seta de ir → sem giro) (telas com desvio: {len(telas["d"])})', n['ico'] > MIN_ICO and not res['d'], sorted(telas['d']))
        chk(f'E{w} teclado: Enter e Espaço alternam a seta sem abrir painel; anel de foco verde de 2 px ({n["tecla"]} telas; desvios: {len(telas["e"])})', n['tecla'] >= 12 and not res['e'], sorted(telas['e']))
        chk(f'F{w} alvo da seta ≥ {44 if w <= 500 else 24} px sem cobrir outro controle' + ('; botão com nome e seta ≥ 44 px de altura' if w <= 500 else '') + f' (telas com desvio: {len(telas["f"])})', not res['f'], sorted(telas['f']))
        chk(f'G{w} sem erro de JavaScript nem estado que não abriu', not res['err'], res['err'][:6])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas' + (' · ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
