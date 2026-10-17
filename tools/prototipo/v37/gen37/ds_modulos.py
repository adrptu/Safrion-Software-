# -*- coding: utf-8 -*-
"""Paridade do design system por módulo (proprietário, 16/10/2026: "os demais módulos estão com design system diferente do nosso padrão de
excelencia do módulo agrícola. Faça seu melhor e mantenha sempre o padrão para mim não ter que ficar cobrando toda vez"; skill padrao-safrion,
passo 3). Abre cada tela do _render a 1440 × 900, no estado inicial, e mede as regras que a tela de referência do Agrícola cumpre:
  CAB-1   cabeçalho com "‹ Módulo" (VOLTA37) nas telas de módulo
  CAB-2   contexto (fazenda, safra) como texto solto no cabeçalho, fora da faixa de filtros (FIL-01)
  BOT-01  mais de um botão verde no mesmo contexto (cabeçalho ou bloco)
  FIL-01  filtro (Fazenda, Safra, Cultura, Talhão, Filtrar…) fora da faixa comum ou faixa sem o funil
  TAB-07  cartões de resumo (números grandes) acima da lista de trabalho
  TAB-05  botão de ação com texto dentro da célula da tabela (fora do ⋯; link e atalho "… ›" ficam)
  TAB-08  tabela própria sem ⇅ e funil no cabeçalho
  VIS-05  lista do motor sem o modo Cartões (Tabela | Cartões ou seletor de visões)
  VIS-06  lista de cartões própria (fora do motor e das telas de entrada)
Saída: tabela por módulo e por regra e o JSON em DS_MOD_JSON (padrão: docs/integracao/V72/ds-modulos.json no repositório).
Catraca ("mantenha sempre o padrão"): --catraca falha se a contagem de alguma regra em algum módulo passar da base gravada
(ds_modulos_base.json); --grava grava a base atual. Desvio corrigido baixa a base na próxima gravação.
Uso (de gen37/): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B ds_modulos.py [--catraca|--grava]   · RENDER_DIR=<outro render> para comparar."""
import os, sys, json, glob, time, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from areas.maquinas import REDIRECIONA
import ui37

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
SAIDA = os.environ.get('DS_MOD_JSON') or os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'docs', 'integracao', 'V72', 'ds-modulos.json'))
FORA = set(REDIRECIONA) | {'Main.dc.html'}
PAGS = sorted(os.path.basename(f) for f in glob.glob(os.path.join(R, '*.dc.html')) if os.path.basename(f) not in FORA)
NOMES = {i: n for i, (n, _ic, _it) in enumerate(ui37.MENU2)}
# telas fora do menu, pelo prefixo (legado ainda gerado; algumas são abertas por links das telas do menu)
PREFIXO = {'AG': 'Agrícola', 'CA': 'Agrícola', 'IR': 'Agrícola', 'PL': 'Agrícola', 'CO': 'Comercial', 'VE': 'Comercial', 'LO': 'Comercial',
           'SU': 'Suprimentos', 'GE': 'Gestão', 'CF': 'Configurações', 'PT': 'Portal do parceiro', 'MB': 'App de campo', 'IN': 'Mapa e Início',
           'ON': 'Onboarding e backoffice', 'BO': 'Onboarding e backoffice', 'CD': 'Cadastros'}
def modulo(pg):
    i, _ = ui37.menu_item(pg)
    if pg in ('MB-01.dc.html',) or pg.startswith('OS-0424-app'): return 'App de campo', True
    if pg == 'PT-01.dc.html': return 'Portal do parceiro', True
    if pg in ('ON-01.dc.html', 'BO-02.dc.html', 'MOD-OUT.dc.html'): return 'Onboarding e backoffice', True
    if i is not None: return NOMES[i], True
    return PREFIXO.get(pg.split('-')[0].split('.')[0], 'Outros'), False

MEDE = r"""(()=>{
 const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); if(r.width<=1||r.height<=1) return false; const cs=getComputedStyle(e); return cs.visibility!=='hidden'&&cs.display!=='none'&&parseFloat(cs.opacity)>0.05; };
 const n=s=>(s||'').replace(/\s+/g,' ').trim();
 const verde=e=>{ const cs=getComputedStyle(e); return cs.backgroundColor==='rgb(30, 122, 76)'&&!e.closest('.menu-lat,nav[aria-label=Menu],[role=tablist],[role=group],[role=listbox],[aria-pressed]')&&!e.matches('[aria-pressed],[role=tab],[role=option]'); };
 const out={}; const main=document.querySelector('main')||document.body; const hd=document.querySelector('header');
 out.h1=n((document.querySelector('h1')||{}).innerText).slice(0,60);
 out.volta=!!document.querySelector('a.volta37,a[aria-label^="Voltar"]');
 const htx=hd?n(hd.innerText):''; out.ctxTexto=!!hd&&/Fazenda Santa Rita|Safra 20\d\d\/\d\d/.test(htx)&&!hd.querySelector('.mf-tela');
 // botões verdes por contexto (cabeçalho; cada section do main)
 const ctx=[hd,...main.querySelectorAll('section')].filter(Boolean);
 out.verdes=ctx.map(c=>[...c.querySelectorAll('button,a')].filter(b=>vis(b)&&verde(b)&&(c.tagName!=='HEADER'||!b.closest('section'))&&(c.tagName==='HEADER'||b.closest('section')===c)).map(b=>n(b.innerText).slice(0,28))).filter(v=>v.length>1);
 // FIL-01
 const filt=[...document.querySelectorAll('select,input[type=search]')].filter(vis).filter(s=>{ const l=n((s.getAttribute('aria-label')||'')+' '+((s.closest('label')||{}).innerText||''));
   return /^(Filtrar|Fazenda|Safra|Cultura|Talh)/i.test(l)&&s.type!=='search'&&!s.closest('.mf-tela,.g2caixa,[role=dialog],aside,form,[role=table],table,.agf-agb'); });
 out.filFora=filt.map(s=>n(s.getAttribute('aria-label')||((s.closest('label')||{}).innerText||'')).slice(0,30));
 out.faixaSemFunil=[...document.querySelectorAll('.mf-tela')].filter(vis).filter(f=>!f.querySelector('.mf-rot svg')&&!/^(Trabalhando|Contexto)/i.test(n((f.querySelector('.mf-rot')||{}).innerText))).length;
 // TAB-07: cartões de resumo (número grande) acima da 1ª lista de trabalho
 const lista=[...main.querySelectorAll('[role=table],[aria-label*=Kanban],.g2cartoes')].find(vis);
 if(lista){ const lt=lista.getBoundingClientRect().top; const big=[...main.querySelectorAll('div')].filter(d=>{ if(!vis(d)) return false; const cs=getComputedStyle(d); if(parseFloat(cs.borderTopLeftRadius)<10||cs.borderTopStyle==='none'||d.closest('[role=table],[role=dialog],aside,.g2caixa')) return false;
     const r=d.getBoundingClientRect(); if(r.bottom>lt||r.height>240||r.width>900) return false; return [...d.querySelectorAll('div,span,b')].some(x=>parseFloat(getComputedStyle(x).fontSize)>=20&&[...x.childNodes].some(t=>t.nodeType===3&&/\d/.test(t.textContent))); });
   const fora=big.filter(d=>!big.some(o=>o!==d&&o.contains(d))); out.resumo=fora.length; out.resumoTx=fora.slice(0,4).map(d=>n(d.innerText).slice(0,40)); } else { out.resumo=0; out.resumoTx=[]; }
 // TAB-05: ação com texto na célula
 out.acaoCelula=[...document.querySelectorAll('[role=table][data-g2g] [role=cell] button')].filter(b=>vis(b)&&!b.closest('.g2mais-w,.g2mais-menu')&&!b.matches('.g2car,.g2del,.g2mais,input')&&/[A-Za-zÀ-ÿ]{3}/.test(n(b.innerText))&&!/›\s*$/.test(n(b.innerText))).map(b=>n(b.innerText).slice(0,24));
 out.acaoCelulaN=out.acaoCelula.length; out.acaoCelula=[...new Set(out.acaoCelula)].slice(0,4);
 // TAB-08: tabela própria sem ⇅ e funil
 out.tabPropria=[...document.querySelectorAll('[role=table],table')].filter(t=>vis(t)&&!t.hasAttribute('data-g2g')).filter(t=>{ const h=t.querySelector('[role=columnheader],th'); return h&&!t.querySelector('.g2hb'); }).map(t=>n(t.getAttribute('aria-label')||t.className||'tabela').slice(0,40));
 // VIS-05: lista do motor sem Cartões
 const temCart=!!document.querySelector('[data-modo=cartoes],[data-visao=cartoes],[data-visao-menu=cartoes]')||[...document.querySelectorAll('main button')].some(b=>n(b.innerText)==='Cartões');
 out.semCartoes=temCart?[]:[...document.querySelectorAll('[role=table][data-g2g]')].filter(vis).map(t=>t.getAttribute('data-g2g'));
 // VIS-06: cartões próprios (classe com card/cartao fora do motor e das telas de entrada)
 const cs=[...main.querySelectorAll('[class]')].filter(e=>vis(e)&&typeof e.className==='string'&&/(^|[\s-])(card|cartao|cartoes)(\s|$|-)/.test(e.className)&&!/\bg2cd|\bg2card|\bmod-|\bg2cartoes/.test(e.className));
 out.cartoesProprios=[...new Set(cs.map(e=>e.className.split(/\s+/).find(c=>/card|cartao/.test(c))))].slice(0,4);
 return out; })()"""

PAINEIS = {'PAGR.dc.html', 'PMAN.dc.html', 'PSUP.dc.html', 'PCOM.dc.html'}   # TAB-07: "Indicador em cartão é do Painel" (cartões do painel não são VIS-06)
REGRAS = [('CAB-1', 'cabeçalho sem "‹ Módulo"'), ('CAB-2', 'contexto como texto no cabeçalho'), ('BOT-01', 'mais de um verde no contexto'),
          ('FIL-01', 'filtro fora da faixa comum'), ('TAB-07', 'cartões de resumo sobre a lista'), ('TAB-05', 'ação com texto na célula'),
          ('TAB-08', 'tabela própria sem ⇅/funil'), ('VIS-05', 'lista sem Cartões'), ('VIS-06', 'cartões próprios')]

def desvios(pg, m, menu):
    d = {}
    if menu and not m['volta'] and pg in ui37.VOLTA37: d['CAB-1'] = 'sem ‹ Módulo'
    elif not m['volta'] and not pg.startswith(('MOD-', 'MB-', 'OS-0424-app', 'PT-', 'Main', 'IN-04', 'CD.dc')): d['CAB-1'] = 'sem voltar no cabeçalho'   # telas de entrada (MOD-*, CD) não voltam
    if m['ctxTexto']: d['CAB-2'] = 'Fazenda/Safra em texto no cabeçalho'
    if m['verdes']: d['BOT-01'] = ' | '.join('+'.join(v) for v in m['verdes'])[:120]
    if m['filFora'] or m['faixaSemFunil']: d['FIL-01'] = ', '.join(m['filFora'])[:80] + (f' · {m["faixaSemFunil"]} faixa(s) sem funil' if m['faixaSemFunil'] else '')
    if m['resumo'] and pg not in PAINEIS: d['TAB-07'] = f'{m["resumo"]} cartões acima da lista: ' + ' | '.join(m.get('resumoTx') or [])[:110]
    if m['acaoCelulaN']: d['TAB-05'] = f'{m["acaoCelulaN"]} botões: ' + ', '.join(m['acaoCelula'])
    if m['tabPropria']: d['TAB-08'] = ', '.join(m['tabPropria'])[:100]
    if m['semCartoes']: d['VIS-05'] = ', '.join(m['semCartoes'])[:100]
    if m['cartoesProprios'] and pg not in PAINEIS: d['VIS-06'] = ', '.join(m['cartoesProprios'])
    return d

def cobertura(esperadas, pags, medidas=None):
    """Catraca só vale com o inventário completo: sem página, ou sem uma página da base, ou sem medição de alguma, reprova (S3 do Codex, 6223504783)."""
    if not esperadas: return 'base sem a lista de páginas (_paginas); regrave com --grava'
    if not pags: return 'render sem páginas'
    falta = sorted(set(esperadas) - set(pags))
    if falta: return f'faltam {len(falta)} página(s) da base: ' + ', '.join(falta[:10])
    if medidas is not None and set(medidas) != set(pags): return f'{len(set(pags) - set(medidas))} página(s) sem medição'
    return ''

if __name__ == '__main__':
    BASEJ = os.path.join(HERE, 'ds_modulos_base.json')
    if '--catraca' in sys.argv:
        erro = cobertura(json.load(open(BASEJ)).get('_paginas'), PAGS)
        if erro: print('RESULTADO: FALHOU ' + erro); sys.exit(1)
    p, srv = servir(R); c = Chrome(); J = c.js; BASE = f'http://127.0.0.1:{p}/'; res = {}
    try:
        c.aparelho(1440, 900, 1, False); c.goto(BASE + 'Main.dc.html', .3); J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
        for pg in PAGS:
            c.goto(BASE + pg, 1.0)
            m = J(MEDE) or {}; mod, menu = modulo(pg)
            res[pg] = dict(modulo=mod, menu=menu, h1=m.get('h1', ''), desvios=desvios(pg, m, menu))
    finally:
        c.close(); srv.terminate()
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True); json.dump(res, open(SAIDA, 'w'), ensure_ascii=False, indent=1)
    por = collections.OrderedDict()
    for pg, x in res.items(): por.setdefault((x['modulo'], x['menu']), []).append((pg, x))
    print(f'{"módulo":28} {"menu":5} {"telas":>5} ' + ' '.join(f'{k:>6}' for k, _ in REGRAS))
    for (mod, menu), L in sorted(por.items(), key=lambda kv: (not kv[0][1], kv[0][0])):
        cont = [sum(1 for _, x in L if k in x['desvios']) for k, _ in REGRAS]
        print(f'{mod:28} {"sim" if menu else "não":5} {len(L):>5} ' + ' '.join(f'{n:>6}' for n in cont))
    tot = sum(len(x['desvios']) for x in res.values())
    print(f'TOTAL: {tot} desvios em {sum(1 for x in res.values() if x["desvios"])} de {len(res)} telas · JSON: {SAIDA}')
    conta = {f'{mod}|{"menu" if menu else "fora"}|{k}': sum(1 for _, x in L if k in x['desvios']) for (mod, menu), L in por.items() for k, _ in REGRAS}
    if '--grava' in sys.argv:
        erro = cobertura(PAGS, PAGS, res)
        if erro: print('RESULTADO: FALHOU ' + erro + ' (base não gravada)'); sys.exit(1)
        json.dump(dict(conta, _paginas=sorted(res)), open(BASEJ, 'w'), ensure_ascii=False, indent=1, sort_keys=True); print('base gravada:', BASEJ)
    elif '--catraca' in sys.argv:
        b = json.load(open(BASEJ)); erro = cobertura(b.get('_paginas'), PAGS, res)
        if erro: print('RESULTADO: FALHOU ' + erro); sys.exit(1)
        sob = [f'{k} {b.get(k, 0)}→{n}' for k, n in sorted(conta.items()) if n > b.get(k, 0)]
        print('RESULTADO: ' + ('catraca ok' if not sob else 'SUBIU: ' + '; '.join(sob))); sys.exit(1 if sob else 0)
