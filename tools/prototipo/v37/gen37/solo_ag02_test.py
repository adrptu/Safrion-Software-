# -*- coding: utf-8 -*-
"""Análises de solo (AG-02 · SOLO-01) · teste de navegador do fluxo principal (docs/analise-solo/ESPECIFICACAO.md §8).
Modos (um por vez, cada um abre o Chrome headless do cadc_lib.T):
  desktop  1440 × 1000: menu (D-01); AC-SOLO-06 registrar o laudo de exemplo (LAU-2073), repetir (recusa), chave repetida (já registrado),
           Caio não valida, Ana valida e só então o T7 tem sugestão; AC-SOLO-07 LAU-2048 inconsistente sem "Validar" e correção do K;
           AC-SOLO-15 OS-0502 liberada → "não aplicável"; Por quê com a regra rotulada; água no solo (CAD, repetida recusada, sem CC
           recusada) e a CAD como referência no IR-01; AC-SOLO-18 tabelas com busca, filtro e ordenação; uma ação primária.
  celular  390 × 844: sem rolagem horizontal da página, primária visível, painel do laudo em tela cheia com o original recolhido e a
           primária presa no rodapé; formulário de registro sem estouro.
Uso: env CHROME_BIN=… flock /tmp/cdpC.lock env CDP_GL=1 timeout 900 python3 solo_ag02_test.py [desktop|celular]
Capturas em _probe/solo_ag02_*.png. Dados sintéticos."""
import sys, os, time, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cadc_lib import T
MODOS = [a for a in sys.argv[1:] if a in ('desktop', 'celular')] or ['desktop', 'celular']
PR = os.path.join(HERE, '_probe'); os.makedirs(PR, exist_ok=True)
t = T(); J = t.J
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.CLK=(t,root)=>{ const r=root?[...document.querySelectorAll(root)].filter(VIS).pop():document; if(!r) return 'SEM RAIZ '+root; const els=[...r.querySelectorAll('button,a,summary')].filter(VIS);
  const e=els.find(x=>N(x.innerText)===t)||els.find(x=>N(x.innerText).startsWith(t))||els.find(x=>(x.getAttribute('aria-label')||'')===t); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok'; };
window.ROW=(t,root)=>{ const R=root?[...document.querySelectorAll(root)].filter(VIS).pop():document; const r=[...R.querySelectorAll('[role=row].g2ed')].filter(VIS).find(x=>N(x.innerText).indexOf(t)>=0); if(!r) return 'sem linha '+t; (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); return 'ok'; };
window.ROWINI=(t,root)=>{ const R=root?[...document.querySelectorAll(root)].filter(VIS).pop():document; const r=[...R.querySelectorAll('[role=row].g2ed')].filter(VIS).find(x=>N(x.innerText).indexOf(t)===0); if(!r) return 'sem linha '+t; (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); return 'ok'; };
window.ROWTXT=(t,root)=>{ const R=root?[...document.querySelectorAll(root)].filter(VIS).pop():document; const r=[...R.querySelectorAll('[role=row]')].find(x=>N(x.innerText).indexOf(t)>=0); return r?N(r.innerText):''; };
window.PANS=()=>[...document.querySelectorAll('aside[role=dialog]')].filter(VIS).map(a=>N(a.innerText));
window.PAN=()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].filter(VIS).pop(); return a?N(a.innerText):''; };
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.ALERT=()=>[...document.querySelectorAll('aside [role=alert]')].filter(VIS).map(x=>N(x.innerText)).join(' | ');
window.PRIMS=()=>[...document.querySelectorAll('header button,header a')].filter(e=>VIS(e)&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)').map(e=>N(e.innerText));
window.SETV=(sel,val)=>{ const i=[...document.querySelectorAll(sel)].filter(VIS).pop()||document.querySelector(sel); if(!i) return 'sem '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
'ok'"""
def lib(): J(LIB)
def ir(pg, w=1440, h=1000, limpa=False, perfil=None):
    t.c.size(w, h)
    if limpa or perfil:
        t.goto('Main.dc.html')
        if limpa: J("localStorage.clear(); sessionStorage.clear()")
        if perfil: J(f"localStorage.setItem('safrion.perfilDemo',{json.dumps(perfil)})")
    t.goto(pg); time.sleep(.6); lib()
def clk(x, root=None, w=.45): r = J(f"CLK({json.dumps(x)},{json.dumps(root)})"); time.sleep(w); return r
def row(x, root=None, w=.5): r = J(f"ROW({json.dumps(x)},{json.dumps(root)})"); time.sleep(w); return r
def rowtxt(x, root=None): return J(f"ROWTXT({json.dumps(x)},{json.dumps(root)})") or ''
def pan(): return J("PAN()") or ''
def toast(): return J("TOAST()") or ''
def alert(): return J("ALERT()") or ''
def setv(sel, val): r = J(f"SETV({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.25); return r
def shot(n): t.c.shot(os.path.join(PR, 'solo_ag02_' + n + '.png'))
def esc(): J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].filter(VIS).pop(); if(a) a.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));})()"); time.sleep(.4)

try:
    if 'desktop' in MODOS:
        print('== desktop · AG-02 Análises de solo')
        ir('AG-02.dc.html', limpa=True, perfil='Ana')
        menu = J("[...document.querySelectorAll('nav a, aside a, .ml-sub a')].map(a=>N(a.innerText)).filter(Boolean)") or []
        i_pa, i_as, i_sf = [menu.index(x) if x in menu else -1 for x in ('Planos agronômicos', 'Análises de solo', 'Planejar safra')]
        t.chk('D-01 menu Agrícola: Análises de solo entre Planos agronômicos e Planejar safra', 0 <= i_pa < i_as < i_sf, menu[:14])
        t.chk('cabeçalho: "1 inconsistente · 1 aguardando validação" e uma só ação primária (Registrar laudo)', '1 inconsistente · 1 aguardando validação' in t.header() and J("PRIMS()") == ['Registrar laudo'], [t.header(), J("PRIMS()")])
        nb = J("[...document.querySelectorAll('[role=table]')].slice(0,2).map(tb=>{ const g=tb.closest('section')||tb.parentElement; return [!!g.querySelector('input[placeholder^=\"Buscar\"]'), g.querySelectorAll('[role=columnheader]').length, (g.innerText.match(/▾/g)||[]).length]; })")
        t.chk('AC-SOLO-18 laudos e água no solo com busca, filtro por coluna e ordenação', nb and all(x[0] and x[2] >= 5 for x in nb), nb)
        o1 = J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].map(r=>N(r.innerText).split(' ')[0])")
        t.chk('lista ordenada pela coleta (mais recente primeiro): LAU-2050 (19/09) antes de LAU-2043 (12/09)', o1 and o1.index('LAU-2050') < o1.index('LAU-2043'), o1)
        t.chk('V "não calculável" no LAU-2050 (sem H+Al) e "difere do laboratório" no LAU-2071', 'não calculável' in rowtxt('LAU-2050') and 'difere do laboratório' in rowtxt('LAU-2071'), [rowtxt('LAU-2050'), rowtxt('LAU-2071')])
        t.chk('No plano: LAU-2061 com 2 sugestões; LAU-2043 (por zona) sem sugestão; LAU-2048 (folha) —', '2 sugestões' in rowtxt('LAU-2061') and 'sem sugestão' in rowtxt('LAU-2043') and rowtxt('LAU-2048').endswith('—'), [rowtxt('LAU-2061'), rowtxt('LAU-2043'), rowtxt('LAU-2048')])
        # ---- AC-SOLO-07: LAU-2048 inconsistente, sem Validar; corrigir o K
        row('LAU-2048'); p = pan()
        t.chk('AC-SOLO-07 LAU-2048 Inconsistente: painel sem "Validar laudo" e o próximo passo diz o que corrigir', 'Inconsistente' in p and 'Validar laudo' not in p and 'Corrija a unidade de K' in p, p[:400])
        J("ROWINI('K ','aside[role=dialog]')"); time.sleep(.5); FV = 'aside[aria-label^="Valor do laudo"]'
        f0 = J(f"(()=>{{const a=document.querySelector({json.dumps(FV)}); if(!a) return null; const r=a.getBoundingClientRect(); return [N(a.innerText).slice(0,40), document.elementFromPoint(r.left+r.width/2, r.top+40)===a||a.contains(document.elementFromPoint(r.left+r.width/2, r.top+40))];}})()")
        t.chk('o formulário de correção abre por cima do painel do laudo (visível e clicável)', f0 and f0[1], f0)
        setv(FV + ' select[id$="_un"]', 'g/kg'); clk('Salvar', FV); time.sleep(.4)
        t.chk('AC-SOLO-07 K corrigido para g/kg → Aguardando validação; o original do PDF não muda', 'corrigido para 17,4 g/kg' in toast() and 'Aguardando validação' in pan() and 'Validar laudo' in pan(), [toast(), pan()[:300]])
        clk('Fechar', 'aside[role=dialog]')
        # ---- AC-SOLO-06: registrar o LAU-2073 (exemplo do T7)
        clk('Registrar laudo'); p0 = pan()
        clk('Preencher com o laudo de exemplo', 'aside[role=dialog]'); clk('Registrar laudo', 'aside[role=dialog]', .7)
        p = pan()
        t.chk('AC-SOLO-06 registrar o laudo de exemplo → LAU-2073 em Aguardando validação, painel aberto nele', 'Registrar laudo de solo' in p0 and 'LAU-2073 · T7 · 0–20 cm' in p and 'Aguardando validação' in p and 'LAU-2073 registrado' in toast(), [p0[:120], p[:200], toast()])
        t.chk('AC-SOLO-06 antes de validar o T7 não tem sugestão (sem uso no plano)', 'Uso no plano' not in p, p[-300:])
        clk('Fechar', 'aside[role=dialog]')
        clk('Registrar laudo'); clk('Preencher com o laudo de exemplo', 'aside[role=dialog]'); clk('Registrar laudo', 'aside[role=dialog]', .6)
        t.chk('AC-SOLO-06 registrar de novo a mesma amostra → recusado "já registrada como LAU-2073"; nada gravado', 'já está registrada como LAU-2073' in alert() and J("Object.keys(__solo.get().laudos).length") == 1, [alert(), J("Object.keys(__solo.get().laudos)")])
        clk('Cancelar', 'aside[role=dialog]'); a = alert(); r_ = clk('Descartar alterações', 'aside[role=dialog]', .6); ps = J("PANS()")
        t.chk('cancelar com alterações avisa e descarta', 'Há alterações não salvas' in a and not ps, [a, r_, ps])
        d = J("(()=>{ const x=Object.assign(__solo.exemplo(),{tal:'T3',area:96}); const a=__solo.registrar(x,'K-DUP-1'); const b=__solo.registrar(x,'K-DUP-1'); return [a.id||a.erro, b.msg||b.erro, Object.keys(__solo.get().laudos).length]; })()")
        t.chk('R13 duplo clique (mesma chave): o segundo devolve "Já registrado" e não cria outro laudo', d and d[0] == 'LAU-2074' and str(d[1]).startswith('Já registrado') and d[2] == 2, d)
        # Caio não valida; Ana valida
        ir('AG-02.dc.html#LAU-2073', perfil='Caio'); time.sleep(.4); p = pan()
        clk('Validar laudo', 'aside[role=dialog]'); a = alert()
        t.chk('AC-SOLO-06 Caio não valida ("decisão de Ana (agrônoma)"); continua Aguardando validação', 'decisão de Ana (agrônoma)' in a and 'Aguardando validação' in pan(), [a, p[:200]])
        ir('AG-02.dc.html#LAU-2073', perfil='Ana'); time.sleep(.4)
        clk('Validar laudo', 'aside[role=dialog]', .7); p = pan()
        t.chk('AC-SOLO-06 Ana valida: Validado e o T7 passa a ter "incluir 0,40 t/ha" disponível no plano', 'LAU-2073 validado por Ana (agrônoma)' in toast() and 'Validado' in p and 'incluir 0,40 t/ha' in p and 'disponível' in p and 'Ver no plano' in p, [toast(), p[-500:]])
        href = J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog] a')].find(a=>N(a.innerText)==='Ver no plano'); return a?a.getAttribute('href'):'';})()")
        t.chk('"Ver no plano" abre o Planejar safra na safra, etapa 2, com as sugestões', href == 'SAF.dc.html#saf=S2627&passo=cultivos&sug=1', href)
        clk('Fechar', 'aside[role=dialog]')
        # ---- Por quê (AG-02): regra rotulada, conta, Esc devolve
        row('LAU-2061'); row('T1-A', 'aside[role=dialog]'); p = pan()
        t.chk('Por quê: laudo, entradas (K 58,65 → médio; meta 3.840 kg/ha), regra "Demonstração — tabela regional…" e a conta 90 ÷ 0,6 = 150',
              'Demonstração — tabela regional a decidir pelo proprietário' in p and '58,65 mg/dm³ (Mehlich-1) → médio' in p and '3.840 kg/ha' in p and '90 ÷ 0,6 = 150' in p and '+4.800 kg' in p, p[:900])
        t.chk('Por quê no AG-02: sem "Usar"; só o link "Ver no plano"', 'Usar' not in p and 'Ver no plano' in p, p[-200:])
        esc(); t.chk('Esc fecha o Por quê e volta ao painel do laudo', len(J("PANS()")) == 1 and 'LAU-2061' in pan(), J("PANS()"))
        clk('Fechar', 'aside[role=dialog]')
        # ---- AC-SOLO-15: OS-0502 liberada → "não aplicável"
        J("(()=>{ const c=__solo.cen(); c.ordens['OS-0502'].etapa='Liberadas'; __solo.salvar(c); })()"); time.sleep(.4)
        row('LAU-2071'); p = pan()
        t.chk('AC-SOLO-15 OS-0502 liberada: a calagem do Pivô 12 fica "não aplicável: OS-0502 já liberada"', 'não aplicável: OS-0502 já liberada' in p, p[-500:])
        clk('Fechar', 'aside[role=dialog]')
        J("(()=>{ const c=__solo.cen(); c.ordens['OS-0502'].etapa='A liberar'; __solo.salvar(c); })()")
        # ---- água no solo
        clk('+ Registrar medição'); f0 = pan()
        for k, v in [('faz', 'Lagoa Grande')]: t.fset(k, v)
        time.sleep(.3)
        for k, v in [('talv', 'Pivô 12'), ('datav', '2026-09-22'), ('profv', '0–40'), ('z', '40'), ('metv', 'Curva de retenção (laboratório)'), ('un', '% volume'), ('ccv', '30'), ('pmpv', '16'), ('fontev', 'Agrolab')]: t.fset(k, v)
        live = t.fv('cadT')
        t.btn('Salvar'); time.sleep(.4)
        t.chk('água no solo: registrar a medição do Pivô 12 → AGS-005 com CAD 56 mm (prévia no formulário)', 'AGS-005' in rowtxt('AGS-005') and '56 mm' in rowtxt('AGS-005') and 'CAD 56 mm' in toast() and '= 56 mm' in (live or ''), [f0[:80], live, rowtxt('AGS-005'), toast()])
        clk('+ Registrar medição'); t.fset('faz', 'Lagoa Grande'); time.sleep(.3)
        for k, v in [('talv', 'Pivô 12'), ('datav', '2026-09-22'), ('profv', '0–40'), ('z', '40'), ('metv', 'Curva de retenção (laboratório)'), ('ccv', '30'), ('pmpv', '16'), ('fontev', 'Agrolab')]: t.fset(k, v)
        t.btn('Salvar'); a = t.alerts()
        t.chk('medição repetida é recusada junto ao campo e nada é gravado', 'já está registrada como AGS-005' in a and t.isopen(), a)
        t.fset('ccv', ''); t.btn('Salvar'); a = t.alerts()
        t.chk('sem capacidade de campo: recusado junto ao campo', 'capacidade de campo' in a.lower(), a)
        t.cancel()
        shot('desktop')
        ir('IR-01.dc.html'); J("SETV('select[aria-label=\"Filtrar por fazenda\"]','Santa Rita')"); time.sleep(.5); lib()
        row('Gotejo T7'); d = t.dlg()
        t.chk('IR-01: a CAD do talhão aparece como referência no setor (T7: 56 mm), dizendo que não é a lâmina', 'Água disponível no solo (referência)' in d and t.fv('cadT') and 'CAD 56 mm' in t.fv('cadT') and 'não é' in d.lower(), [t.fv('cadT'), d[-300:]])
        t.cancel()
        t.chk('nenhum erro de JS (desktop)', not t.errs(), t.errs())
    if 'celular' in MODOS:
        print('== celular · 390 × 844')
        ir('AG-02.dc.html', 390, 844, limpa=True, perfil='Ana')
        sw = J("[document.documentElement.scrollWidth, window.innerWidth]")
        t.chk('AC-SOLO-18 390 px: sem rolagem horizontal da página', sw and sw[0] <= sw[1] + 1, sw)
        pv = J("(()=>{ const b=[...document.querySelectorAll('header button')].find(b=>N(b.innerText)==='Registrar laudo'); if(!b) return null; const r=b.getBoundingClientRect(); return [r.top>=0&&r.bottom<=innerHeight, Math.round(r.height)]; })()")
        t.chk('primária "Registrar laudo" visível no celular', pv and pv[0], pv)
        row('LAU-2063'); time.sleep(.3)
        g = J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].filter(VIS).pop(); if(!a) return null; const r=a.getBoundingClientRect(); const d=a.querySelector('.so-orig-d'), m=a.querySelector('details.so-orig-m');"
              " const pb=[...a.querySelectorAll('.so-pe a,.so-pe button')].filter(VIS).map(e=>{ const q=e.getBoundingClientRect(); return [N(e.innerText), q.bottom<=innerHeight+1, Math.round(q.height)]; });"
              " return [Math.round(r.width), VIS(d), VIS(m), m?m.open:null, pb, a.scrollWidth<=a.clientWidth+1]; })()")
        t.chk('painel do laudo em tela cheia; original recolhido em "Ver original"; primária presa no rodapé com 44 px; sem estouro lateral',
              g and g[0] >= 388 and not g[1] and g[2] and g[3] is False and any(x[0] == 'Ver no plano' and x[1] and x[2] >= 44 for x in g[4]) and g[5], g)
        shot('celular_laudo')
        clk('Fechar', 'aside[role=dialog]'); clk('Registrar laudo'); clk('Preencher com o laudo de exemplo', 'aside[role=dialog]')
        g = J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].filter(VIS).pop(); return a?[a.scrollWidth<=a.clientWidth+1, Math.round(a.getBoundingClientRect().width)]:null; })()")
        t.chk('formulário de registro a 390 px sem estouro lateral', g and g[0] and g[1] >= 388, g)
        shot('celular_registro')
        t.chk('nenhum erro de JS (celular)', not t.errs(), t.errs())
finally:
    t.fim()
