# -*- coding: utf-8 -*-
"""PLAT-01 · teste de navegador do CF-05 Assinatura e cobrança (ESPECIFICACAO.md §8: A3, A4, A5, A7, A8, A9, A10, A11, A13, A14, A15, A16, A17, A18).
Fluxo principal em desktop (1440 × 900) e no celular (390 × 844, toque): normal (prévia → aceite → fechamento → pagar), erro/recusa
(área abaixo da medida e acima de 5.000 ha, pagar sem forma, talhão novo com a assinatura inadimplente) e repetição (aceite e pagamento
repetidos sem segundo efeito). Faixa de cobrança nas telas da organização (OS, EST, CD-01) e em nenhuma outra (MB-01, CF-05, BO-02, ON-01).
Revisão PLAT (06/10): medida do período = maior entre abertura e fechamento (A7b, A4d, A18c), uma contestação por fatura e quem age nos
eventos (A17c, A6), proposta empresarial acima de 5.000 ha (A20), faixa curta no celular (A15e), nenhuma faixa no PT (A8c).
Trava (R12): Cadastrar talhão e Desenhar recusam antes de abrir; Reativar recusa ao salvar; importação recusa a linha "Talhão novo" e importa o
contorno novo de talhão existente; editar a área de talhão existente salva; liberar O.S. segue. Contestação congela a régua; crédito vai para o
período seguinte. Uso (de gen37/, depois de build.py e montar_render.py): python3 assinatura_test.py   (CDP_GL=1 para o mapa real)"""
import sys, os, time, json, tempfile
os.environ.setdefault('CDP_GL', '1')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, MEDE
import dados_lagoa_fonte as LF
PROBE = os.path.join(HERE, '_probe'); os.makedirs(PROBE, exist_ok=True)
OK = []; FA = []
def cad_mais(t):
    import dados_assinatura as DA
    b = DA.cad0(); return dict(faz=b['faz'], tal=b['tal'] + [t])
def chk(n, c, info=''):
    (OK if c else FA).append(n); print(('OK   ' if c else 'FALHA'), n, ('' if c else '· ' + str(info)[:900]), flush=True)
p, srv = servir(os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')); c = None; ERRL = []
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
VIS = "(e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; })"
PRIMS = f"(()=>{{const n={N}, vis={VIS}; return [...document.querySelectorAll('header button,header a,main button,main a')].filter(e=>vis(e)&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)'&&!e.closest('.menu-lat')).map(e=>n(e.innerText));}})()"
def J(x): return c.js(x)
def errs(): return [e for e in (J("window.__errs||[]") or []) if "reading 'g2toast'" not in e]
def go(pg, hash='', limpa=False):
    if c.alvo: ERRL.extend(errs())
    c.goto(f'http://127.0.0.1:{p}/{pg}{hash}')
    if limpa: J("localStorage.clear(); sessionStorage.clear(); 1"); c.goto(f'http://127.0.0.1:{p}/{pg}{hash}')
    time.sleep(.4)
def body(): return J("document.body.innerText") or ''
def espera(js, ate=20.0):
    """espera a condição observável (página nova pronta), não um tempo fixo; no limite devolve False e a verificação falha"""
    t0 = time.time()
    while time.time() - t0 < ate:
        try:
            if J(js): return True
        except Exception: pass
        time.sleep(.1)
    return False
def pronta(pg, extra='true'): return f"location.pathname.endsWith('/{pg}') && document.readyState==='complete' && !!document.body && ({extra})"
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def dlg(): return J(f"(()=>{{const d=[...document.querySelectorAll('aside[role=dialog]')].find({VIS}); return d?d.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def clk(t, root='', vez=1):
    r = J(f"""(()=>{{const n={N}, vis={VIS}; const R=[...document.querySelectorAll({json.dumps(root or 'body')})].filter(vis).pop()||document.body;
      const es=[...R.querySelectorAll('button,a')].filter(e=>vis(e)&&!e.disabled); const e=es.find(x=>n(x.innerText)===n({json.dumps(t)}))||es.find(x=>n(x.innerText).startsWith(n({json.dumps(t)})));
      if(!e) return 'sem '+{json.dumps(t)}; for(let i=0;i<{vez};i++) e.click(); return 'ok';}})()""")
    time.sleep(.5); return r
def setv(sel, val):
    J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); if(!i) return 0; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
      Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}})); return 1;}})()"""); time.sleep(.3)
def tabela(i): return J(f"(()=>{{const t=document.querySelectorAll('main [role=table]')[{i}]; return t?t.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def linha(i, txt): return J(f"(()=>{{const t=document.querySelectorAll('main [role=table]')[{i}]; const r=t&&[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def abre_linha(i, txt):
    r = J(f"(()=>{{const t=document.querySelectorAll('main [role=table]')[{i}]; const r=t&&[...t.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); if(!r) return 'sem linha'; (r.querySelector('[role=cell]')||r).click(); return 'ok';}})()")
    time.sleep(.5); return r
def faixa(): return J("(()=>{const f=document.querySelector('header [aria-label=Cobrança]'); if(!f) return null; const a=f.querySelector('a'); return {t:f.innerText.replace(/\\s+/g,' '),href:a&&a.getAttribute('href'),bg:getComputedStyle(f).backgroundColor,link:a?getComputedStyle(a).backgroundColor:''};})()")
def data(d): return clk(d)
def selo(): return J("(()=>{const h=document.querySelector('header h1'); const s=h&&h.nextElementSibling; return s?s.innerText.trim():'';})()") or ''
ALERTA = "(()=>{const a=[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText.trim()).filter(Boolean); return a.join(' | ');})()"
CAMPO_PAG = "[...document.querySelectorAll('input,textarea,select')].map(i=>[i.getAttribute('aria-label'),i.id,i.name,i.placeholder,i.getAttribute('autocomplete')].join(' ')).filter(t=>/cart|card|cpf|cnpj|conta|ag[eê]ncia|cvv|cvc|validade|cc-/i.test(t))"
try:
    c = Chrome(); c.aparelho(1440, 900)
    # ============ cenário A · 23/09: menu, estado, uma primária, grades, prévia, aceite, desfazer, talhão de 50 ha ============
    go('CF-05.dc.html', limpa=True)
    # navegação sem submenus (13/10/2026, ui37.MENU2/HUB37/CURTO37): barra só com ícones (aria-label = módulo) e, por último, "Outros acessos";
    # o ícone Configurações abre a tela de entrada e o cartão "Assinatura" abre esta tela (antes: o subitem "Assinatura e cobrança")
    m = J("""(()=>{const n=document.querySelector('nav[aria-label=Menu]'); const as=[...n.querySelectorAll('a[aria-label]')].filter(a=>a.closest('.ml-topo')===null);
      return {it:as.map(a=>a.getAttribute('aria-label')), cfg:as.filter(a=>a.getAttribute('aria-label')==='Configurações').map(a=>a.getAttribute('href')),
        mapa:as.filter(a=>a.getAttribute('aria-label')==='Mapa').map(a=>a.getAttribute('href')), atual:as.filter(a=>a.getAttribute('aria-current')==='page').map(a=>a.getAttribute('aria-label'))};})()""")
    ERRL.extend(errs()); J("document.querySelector('nav[aria-label=Menu] a[aria-label=\"Configurações\"]').click()")
    m['hub'] = espera(pronta('MOD-CFG.dc.html', "document.querySelectorAll('a.mod-cartao').length>0"))
    m['cartoes'] = J("[...document.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length).map(a=>[a.getAttribute('href'),a.innerText.replace(/\\s+/g,' ').trim()])") or []
    ERRL.extend(errs()); m['clk'] = clk('Assinatura', '.mod-grade')
    m['volta'] = espera(pronta('CF-05.dc.html', "!!document.querySelector('header h1') && document.querySelectorAll('main [role=table]').length>0")); time.sleep(.4)
    m['h1'] = J("(document.querySelector('header h1')||{innerText:''}).innerText.trim()")
    chk('A16 navegação: Configurações é o último módulo da barra (antes de Outros acessos), marcado nesta tela; o ícone abre a tela de entrada e o cartão "Assinatura" abre "Assinatura e cobrança"; Mapa segue link único',
        m['it'][-2:] == ['Configurações', 'Outros acessos'] and m['cfg'] == ['MOD-CFG.dc.html'] and m['atual'] == ['Configurações'] and m['hub']
        and [x for x in m['cartoes'] if x[0] == 'CF-05.dc.html'] == [['CF-05.dc.html', 'Assinatura']] and m['clk'] == 'ok' and m['volta'] and m['h1'] == 'Assinatura e cobrança'
        and m['mapa'] == ['IN-04.dc.html'], m)
    b = body()
    chk('A7a 23/09: selo Ativa; resumo Completo · 2.570,23 ha de 2.600 ha · R$ 5.140,46 (set/2026 fecha em 30/09) · próxima 01/10/2026',
        selo() == 'Ativa' and all(x in b for x in ('Completo', '2.570,23 ha', 'de 2.600 ha contratados', 'R$ 5.140,46', 'set/2026 fecha em 30/09', '01/10/2026')), [selo(), b[:600]])
    chk('A11a uma primária (verde cheio) em repouso: Alterar plano ou área', J(PRIMS) == ['Alterar plano ou área'], J(PRIMS))
    g = J("""(()=>[...document.querySelectorAll('main .g2caixa')].map(x=>({busca:!!x.querySelector('input[type=search]'),ord:x.querySelectorAll('.g2hb').length,fil:x.querySelectorAll('.g2fb').length,linhas:x.querySelectorAll('[role=row]').length})))()""")
    chk('A14a as 3 grades (uso, faturas, planos) têm busca, ordenação e filtro por coluna', len(g) == 3 and all(x['busca'] and x['ord'] >= 4 and x['fil'] >= 4 for x in g), g)
    chk('A14b unidade na célula: "312 ha" no uso, "R$ 2.330,00" nas faturas, total 2.570,23 ha no rodapé', '312 ha' in tabela(0) and 'R$ 2.330,00' in tabela(1) and '2.570,23 ha' in tabela(0), [tabela(0)[:200], tabela(1)[:200]])
    chk('A14c filtro rápido por fazenda e ordenação padrão por área decrescente (1ª linha T1 312 ha)', J("[...document.querySelectorAll('main .g2caixa')][0].innerText.indexOf('Lagoa Grande')>=0") and 'T1' in (J("(()=>{const r=document.querySelectorAll('main [role=table]')[0].querySelectorAll('[role=row]')[1]; return r?r.innerText:'';})()") or ''))
    chk('A13a CF-05 sem cultura e sem safra (nenhum nome de cultura nem 2026/27)', not any(x in b for x in ('Soja', 'Milho', 'Feijão', 'Café', 'Mamão', '2026/27')))
    chk('A18a nenhum campo de cartão, conta ou documento no CF-05', J(CAMPO_PAG) == [], J(CAMPO_PAG))
    chk('A8a sem faixa de cobrança no próprio CF-05', faixa() is None)
    # prévia e aceite pela linha do plano
    abre_linha(2, 'Essencial'); d = dlg()
    chk('A4a prévia hoje → depois: R$ 5.140,46 → R$ 3.855,35, −R$ 1.285,11/mês, R$ 18,00/ha·ano, início 01/10/2026, sem fidelidade',
        all(x in d for x in ('R$ 5.140,46 → R$ 3.855,35', '−R$ 1.285,11', 'R$ 18,00/ha·ano', '01/10/2026', 'sem fidelidade', 'saem: Pós-colheita')), d[:900])
    setv('#cf_pha', '100'); clk('Aceitar e agendar para 01/10/2026', 'aside[role=dialog]'); a1 = J(ALERTA)
    setv('#cf_pha', '9.000'); clk('Aceitar e agendar para 01/10/2026', 'aside[role=dialog]'); a2 = J(ALERTA)
    chk('A5 recusa com o motivo: abaixo da medida (100 ha) e acima de 5.000 ha; nada agendado', 'não pode ficar abaixo da medida hoje (2.570,23 ha)' in a1 and 'Acima de 5.000 ha: proposta empresarial' in a2 and 'agendad' not in dlg().lower(), [a1, a2])
    setv('#cf_pha', '2.600'); clk('Aceitar e agendar para 01/10/2026', 'aside[role=dialog]', vez=2); t = toast(); d = dlg()
    chk('A4b aceite (clique duplo): um contrato v3 agendado; o 2º clique devolve o mesmo recibo ACE-0001; o botão some (form igual ao agendado)',
        ('Aceite registrado (ACE-0001): contrato v3 · Essencial' in t or 'Aceite já registrado · ACE-0001' in t) and 'Mudança agendada: Essencial · 2.600 ha a partir de 01/10/2026' in d and 'Aceitar e agendar' not in d and J("JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).assin.orgs.sr.contratos.length") == 3, [t, d[-400:]])
    clk('Desfazer mudança', 'aside[role=dialog]'); t = toast()
    chk('A4c desfazer antes de 01/10 volta ao contrato v2 (com recibo DES-0001: desfazer também registra quem agiu, revisão PLAT achado 4)', 'Mudança desfeita (DES-0001): segue Completo' in t and 'Seu plano' in linha(2, 'Completo'), t)
    clk('Fechar', 'aside[role=dialog]')
    # talhão novo de 50 ha pelo formulário do CD-01 (A10)
    go('CD-01.dc.html'); clk('Cadastrar talhão')
    setv('#fx_g_tal_t', 'T9'); setv('#fx_g_tal_faz', 'Santa Rita'); setv('#fx_g_tal_sis', 'Sequeiro'); setv('#fx_g_tal_decl', '50'); clk('Salvar', 'aside[role=dialog]'); t = toast()
    go('CF-05.dc.html'); b = body()
    chk('A10a talhão de 50 ha no CD-01: CF-05 mede 2.620,23 ha, avisa 20,23 ha acima do contratado (sem cobrança-surpresa: prévia R$ 5.200,00) e a primária vira Ampliar área contratada',
        'T9 cadastrado' in t and '2.620,23 ha' in b and '20,23 ha acima da área contratada' in b and 'R$ 5.200,00' in b and J(PRIMS) == ['Ampliar área contratada'], [t, J(PRIMS), b[:500]])
    clk('Ampliar área contratada'); d = dlg()
    chk('A10b Ampliar abre a prévia com 2.700 ha: R$ 5.200,00 → R$ 5.240,46', J("document.querySelector('#cf_pha').value") == '2.700' and 'R$ 5.200,00 → R$ 5.240,46' in d, [J("document.querySelector('#cf_pha').value"), d[:600]])
    clk('Fechar', 'aside[role=dialog]')
    go('BO-02.dc.html'); b = body()
    chk('A10c BO-02 mede ao vivo: Grupo Santa Rita 2.620,23 ha e mensalidades vigentes R$ 6.338,00', '2.620,23 ha' in linha(0, 'Grupo Santa Rita') and 'R$ 6.338,00' in b, [linha(0, 'Grupo Santa Rita'), b[:300]])
    # ============ cenário B · datas, faixa, trava, pagamento ============
    # B1 (Boa Vista, sem parcela em safra aberta) é o talhão que dá para inativar; os da Santa Rita têm parcelas (o CD-01 recusa inativar)
    go('CD-01.dc.html', limpa=True); abre_linha(0, 'B1'); setv('#fx_g_tal_sit', 'Inativo'); clk('Salvar', 'aside[role=dialog]'); t0 = toast()
    go('CF-05.dc.html'); clk('Alterar plano ou área'); clk('Essencial', 'aside[role=dialog]'); clk('Aceitar e agendar para 01/10/2026', 'aside[role=dialog]'); clk('Fechar', 'aside[role=dialog]')
    data('01/10/2026'); t = toast(); b = body()
    # revisão PLAT, achado 3: a medida do período é a maior entre a abertura (01/09: 2.570,23 ha) e o fechamento (2.450,23 ha com B1 inativo);
    # antes este teste aceitava fechar com 2.450,23 ha → R$ 4.900,46, o que deixava inativar antes do fechamento e reativar depois fora da cobrança
    chk('A7b 01/10: set/2026 fecha com a medida da abertura (2.570,23 ha; 2.450,23 ha no fechamento, B1 inativo) e vence hoje; primária Pagar fatura; out/2026 já no Essencial',
        'B1 inativo' in t0 and 'set/2026 fechou com 2.570,23 ha (medida da abertura, 2.450,23 ha no fechamento) → R$ 5.140,46' in t and J(PRIMS) == ['Pagar fatura'] and 'A vencer' in linha(1, 'set/2026') and 'Essencial' in b, [t0, t, J(PRIMS), linha(1, 'set/2026')])
    abre_linha(1, 'set/2026'); d = dlg()
    chk('A4d a fatura de set/2026 fechou no Completo (mudança nunca retroage); memória com a medida do período (abertura × fechamento), mín(medida; contratada), quem aceitou o contrato e "pela área contratada seria"',
        'Completo · R$ 2,00/ha·mês' in d and 'maior entre a abertura (01/09: 2.570,23 ha) e o fechamento (30/09: 2.450,23 ha)' in d and 'mín(medida; contratada) = 2.570,23 ha' in d
        and 'contrato v2 · aceite por Ana · Gestora' in d and 'Pela área contratada seria R$ 5.200,00' in d, d[:1200])
    clk('Fechar', 'aside[role=dialog]')
    data('06/10/2026')
    chk('A7c 06/10: Em atraso · 5 dias', selo() == 'Em atraso · 5 dias', selo())
    fx = {}
    for pg in ('OS.dc.html', 'EST.dc.html', 'CD-01.dc.html'):
        go(pg); fx[pg] = faixa()
    chk('A8b faixa amarela em OS, EST e CD-01 (sem cenario.js): "vencida há 5 dias (data simulada da cobrança: 06/10)", link de texto Pagar fatura → CF-05#pagar',
        all(f and 'vencida há 5 dias (data simulada da cobrança: 06/10)' in f['t'] and 'nada está restrito' in f['t'] and f['href'] == 'CF-05.dc.html#pagar' and f['bg'] == 'rgb(255, 243, 214)'
            and f['link'] != 'rgb(30, 122, 76)' for f in fx.values()), fx)
    sem = {}
    for pg in ('MB-01.dc.html', 'BO-02.dc.html', 'ON-01.dc.html', 'PT-01.dc.html', 'CF-05.dc.html'):
        go(pg); sem[pg] = faixa() is None and 'vencida há' not in (J("(document.querySelector('header')||document.body).innerText") or '')
    chk('A8c nenhuma faixa no app (MB-01), na plataforma (BO-02), no onboarding (ON-01), no portal do parceiro (PT-01) nem no CF-05', all(sem.values()), sem)
    data('16/10/2026')
    chk('A7d 16/10: Inadimplente · 15 dias', selo() == 'Inadimplente · 15 dias', selo())
    go('OS.dc.html'); f = faixa()
    chk('A8d faixa vermelha na O.S.: suspenso ampliar a área, nada apagado, trabalho de campo segue', f and f['bg'] == 'rgb(253, 232, 230)' and 'suspenso' in f['t'] and 'nada foi apagado' in f['t'], f)
    lib = J("(()=>{ const C=window.__cen; if(!C) return 'sem window.__cen'; const r=C.cenMudar(null,k=>C.osc_liberar(k,'OS-0430',false,'',{k:'Ana'})); return r.erro||r.msg||''; })()")
    chk('A9a inadimplente: liberar a OS-0430 (mesmo comando da tela, osc_liberar) segue', 'liberada' in (lib or ''), lib)
    go('CD-01.dc.html'); clk('Cadastrar talhão'); t = toast()
    chk('A9b Cadastrar talhão recusa antes de abrir, com motivo e caminho', 'suspenso até o pagamento' in t and 'Configurações › Assinatura e cobrança' in t and dlg() == '', [t, dlg()[:200]])
    abre_linha(0, 'T4'); setv('#fx_g_tal_decl', '205'); clk('Salvar', 'aside[role=dialog]'); t = toast()
    chk('A9c editar a área cultivável de um talhão existente salva (corrigir o fato não é ampliar o contrato)', 'Salvo: T4' in t and dlg() == '', [t, dlg()[:300]])
    abre_linha(0, 'B1'); setv('#fx_g_tal_sit', 'Ativo'); clk('Salvar', 'aside[role=dialog]'); a = J(ALERTA) or dlg()
    chk('A9d Reativar B1 recusado ao salvar (CD-01)', 'suspenso' in a and 'B1' in J("JSON.stringify(JSON.parse(localStorage.getItem('talhao-os-cd01-v1')).tal.filter(t=>t.id==='B1'&&t.v.sit==='Inativo'))"), a[:300])
    clk('Cancelar', 'aside[role=dialog]'); clk('Descartar alterações', 'aside[role=dialog]')
    go('CD-01det.dc.html', '#talhao=B1'); clk('Reativar B1'); clk('Salvar', 'aside[role=dialog]'); a = dlg()
    chk('A9e Reativar no detalhe (CD-01det) também recusado ao salvar', 'suspenso' in a, a[:300])
    # Mapa (Lagoa Grande): Desenhar recusa antes de abrir; importação: linha "Talhão novo" recusada, contorno de pivô existente importado
    go('IN-04.dc.html')
    fim = time.time() + 60
    while time.time() < fim and not J("!!(window.__LGI&&window.__LGI.pronto)"): time.sleep(.5)
    pronto = J("!!(window.__LGI&&window.__LGI.pronto)")
    if pronto:
        clk('Desenhar'); t = toast(); bar = J("document.body.innerText.indexOf('Clique no primeiro canto do talhão')>=0")
        chk('A9f Desenhar talhão novo recusa antes de abrir o desenho', 'suspenso' in t and not bar, [t, bar])
        pv = [x for x in LF.LG_PIVOS if x[0] == 'PV01'][0]; lon, lat, r = pv[3], pv[4], pv[5]
        k = r * 0.5 / 111320 / max(.1, __import__('math').cos(__import__('math').radians(lat))); kl = r * 0.5 / 110540
        sq = lambda x, y, a, b: [[x - a, y - b], [x + a, y - b], [x + a, y + b], [x - a, y + b], [x - a, y - b]]
        gj = dict(type='FeatureCollection', features=[dict(type='Feature', properties=dict(name='Pivô 1'), geometry=dict(type='Polygon', coordinates=[sq(lon, lat, k, kl)])),
                                                      dict(type='Feature', properties=dict(name='Talhão Leste'), geometry=dict(type='Polygon', coordinates=[sq(lon + 0.2, lat + 0.2, k, kl)]))])
        fd, arq = tempfile.mkstemp(suffix='.geojson'); os.write(fd, json.dumps(gj).encode()); os.close(fd)
        clk('Importar'); time.sleep(.4)
        doc = c.call('DOM.getDocument', {'depth': -1, 'pierce': True}); nid = c.call('DOM.querySelector', {'nodeId': doc['root']['nodeId'], 'selector': 'input[type=file]'})['nodeId']
        c.call('DOM.setFileInputFiles', {'files': [arq], 'nodeId': nid}); time.sleep(1.2)
        sels = J("[...document.querySelectorAll('select[aria-label^=\"Destino de\"]')].map(s=>s.getAttribute('aria-label')+'='+s.value)")
        J("(()=>{const b=[...document.querySelectorAll('button')].filter(x=>/^Importar \\d|^Importar$|^Importar /.test(x.innerText.trim())&&x.closest('aside')); if(b.length) b[b.length-1].click();})()"); time.sleep(.6)
        e1 = J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')") or ''
        setv('select[aria-label="Destino de Talhão Leste"]', 'nao')
        J("(()=>{const b=[...document.querySelectorAll('button')].filter(x=>/^Importar/.test(x.innerText.trim())&&x.closest('aside')); if(b.length) b[b.length-1].click();})()"); time.sleep(.6); t = toast()
        chk('A9g importação: a linha "Talhão novo" é recusada com o motivo; com ela em "Não importar", o contorno novo do Pivô 1 é importado',
            'é talhão novo' in e1 and 'suspenso' in e1 and 'contorno atualizado' in t, [sels, e1[:300], t])
        os.unlink(arq)
    else:
        chk('A9f/A9g mapa real pronto para desenhar e importar', False, J("window.__LGI&&window.__LGI.erro"))
    # pagar pelo atalho da faixa (#pagar): sem forma recusa; clique duplo paga uma vez; CSV com a cópia
    go('CF-05.dc.html', '#pagar'); time.sleep(.4); d = dlg()
    chk('A7e o atalho da faixa (CF-05#pagar) abre a fatura aberta', 'Fatura de set/2026' in d and 'Confirmar pagamento (simulado)' in d, d[:200])
    chk('A18b nenhum campo de cartão, conta ou documento no painel de pagamento (forma escolhida numa lista)', J(CAMPO_PAG) == [] and 'Pix · simulado' in d and 'Cartão final 4242 · simulado' in d, J(CAMPO_PAG))
    clk('Confirmar pagamento (simulado)', 'aside[role=dialog]'); a = J(ALERTA)
    clk('Pix · simulado', 'aside[role=dialog]'); clk('Confirmar pagamento (simulado)', 'aside[role=dialog]', vez=2); t = toast(); d = dlg()
    npg = J("JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).assin.orgs.sr.faturas.find(f=>f.comp==='2026-09').eventos.filter(e=>/^Paga/.test(e.t)).length")
    chk('A6/A7f pagar sem forma é recusado; com Pix (clique duplo) paga uma vez: o 2º clique devolve o mesmo recibo PAG-0001; o evento diz quem pagou; volta a Ativa',
        'Escolha a forma de pagamento' in a and ('Pagamento simulado confirmado' in t or 'Pagamento já registrado · recibo PAG-0001' in t) and 'PAG-0001' in t and npg == 1 and 'Paga' in d
        and 'recibo PAG-0001 · por Ana (gestora)' in d and selo() == 'Ativa', [a, t, npg, selo(), d[-500:]])   # CONF-01 P7: quem age é o perfil (AL-15), no formato dos outros comandos
    clk('Baixar fatura (CSV)', 'aside[role=dialog]'); csv = J("window.__assinCsv||''") or ''
    chk('A18c Baixar fatura (CSV): números da cópia (2.570,23 ha · R$ 5.140,46; fechamento 2.450,23 ha; mesmo depois de editar o T4) e cobrança simulada',
        '"Área medida (ha)";"2.570,23"' in csv and '"Medida no fechamento (ha)";"2.450,23"' in csv and '5.140,46' in csv and 'simulada' in csv, csv[:500])
    clk('Fechar', 'aside[role=dialog]')
    go('CD-01.dc.html'); clk('Cadastrar talhão')
    chk('A9h depois de pagar, Cadastrar talhão volta a abrir o formulário; faixa some', 'Cadastrar talhão' in dlg() and faixa() is None, dlg()[:120])
    # ============ cenário C · contestação congela a régua e resolver com crédito vai para o período seguinte (A17) ============
    go('CF-05.dc.html', limpa=True); data('01/10/2026'); abre_linha(1, 'set/2026'); clk('Contestar fatura', 'aside[role=dialog]')
    setv('#cf_motivo', 'Área da Lagoa Grande contada antes do aceite'); clk('Registrar contestação', 'aside[role=dialog]'); t = toast(); clk('Fechar', 'aside[role=dialog]')
    data('16/10/2026')
    chk('A17a contestada: em 16/10 o selo segue Ativa, a fatura está Em contestação e a primária não é Pagar fatura', 'Contestação registrada' in t and selo() == 'Ativa' and 'Em contestação' in linha(1, 'set/2026') and J(PRIMS) != ['Pagar fatura'], [t, selo(), linha(1, 'set/2026'), J(PRIMS)])
    go('BO-02.dc.html'); abre_linha(0, 'Grupo Santa Rita'); clk('Creditar no próximo período', 'aside[role=dialog]'); setv('#bo_cred', '100,00'); clk('Registrar resolução', 'aside[role=dialog]'); t = toast()
    go('CF-05.dc.html'); b = body()
    chk('A17b resolver com crédito: set/2026 volta a A vencer (vence 21/10, sem reescrever o valor) e out/2026 mostra o crédito de R$ 100,00',
        'Contestação de Grupo Santa Rita resolvida' in t and 'A vencer' in linha(1, 'set/2026') and '21/10/2026' in linha(1, 'set/2026') and 'R$ 5.140,46' in linha(1, 'set/2026') and 'crédito de R$ 100,00' in b, [t, linha(1, 'set/2026'), b[:400]])
    abre_linha(1, 'set/2026'); d = dlg(); bts = J("[...document.querySelectorAll('aside[role=dialog] button')].map(x=>x.innerText.trim())") or []
    chk('A17c (revisão PLAT, achado 1) fatura já contestada e resolvida: sem "Contestar fatura" no painel; eventos dizem quem contestou e quem resolveu',
        'Contestar fatura' not in bts and 'Confirmar pagamento (simulado)' in bts and 'por Ana (gestora): Área da Lagoa Grande' in d and 'Contestação resolvida (RES-0001) · por Admin plataforma' in d, [bts, d[-700:]])
    clk('Fechar', 'aside[role=dialog]')
    # ============ cenário E · medida acima de 5.000 ha (revisão PLAT, achado 10): primária Pedir proposta empresarial, uma vez ============
    # estado injetado no cadastro salvo: o CD-01 recusa talhão acima da área da fazenda; o caso real é uma fazenda grande importada
    go('CF-05.dc.html', limpa=True)
    J('localStorage.setItem("talhao-os-cd01-v1", ' + json.dumps(json.dumps(cad_mais({'id':'TNX','v':{'t':'Grande','faz':'Santa Rita','decl':2600,'sit':'Ativo'}}))) + '); 1')
    go('CF-05.dc.html'); p0 = J(PRIMS)
    clk('Pedir proposta empresarial', vez=2); t = toast(); p1 = J(PRIMS); dis = J("(()=>{const b=[...document.querySelectorAll('header button')].find(x=>/Proposta empresarial pedida/.test(x.innerText)); return b?b.getAttribute('aria-disabled')==='true':null;})()")   # DS-DICA-20261009: indisponível com motivo fica focável (aria-disabled)
    npro = J("Object.values(JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).assin.recibos).filter(r=>/^PRO-/.test(r.id)).length")
    go('BO-02.dc.html'); lsr = linha(0, 'Grupo Santa Rita')
    chk('A20 medida 5.170,23 ha: primária Pedir proposta empresarial (não Ampliar, que seria sempre recusado); clique duplo registra um pedido (PRO-0001); a primária fica desabilitada e o BO-02 mostra o pedido',
        p0 == ['Pedir proposta empresarial'] and ('PRO-0001' in t) and npro == 1 and p1 == ['Proposta empresarial pedida em 23/09'] and dis is True and 'proposta empresarial pedida em 23/09' in lsr, [p0, t, p1, dis, npro, lsr])
    # ============ cenário D · celular 390 px (toque): fluxo principal normal, erro e repetição ============
    c.aparelho(390, 844, 2, True); go('CF-05.dc.html', limpa=True); md = J(MEDE)
    kp = J("getComputedStyle(document.querySelector('.assin-kpis')).gridTemplateColumns.split(' ').length")
    c.shot(os.path.join(PROBE, 'assin_cf05_390.png'))
    chk('A15a 390 px: sem rolagem lateral da página, título e primária alcançáveis, resumo 2 × 2', not md.get('pagLado') and md.get('h1ok') and md.get('prim') == ['Alterar plano ou área'] and not md.get('primRuim') and kp == 2, [md, kp])
    clk('Alterar plano ou área'); md = J(MEDE)
    chk('A15b 390 px: painel do plano dentro da tela, com fechar e primária alcançáveis', md.get('painel') and not md.get('painelFora') and md.get('painelFechar') and md.get('painelPrimOk'), md)
    c.shot(os.path.join(PROBE, 'assin_cf05_390_plano.png'))
    clk('Essencial', 'aside[role=dialog]'); setv('#cf_pha', '100'); clk('Aceitar e agendar para 01/10/2026', 'aside[role=dialog]'); a = J(ALERTA)
    setv('#cf_pha', '2.600'); clk('Aceitar e agendar para 01/10/2026', 'aside[role=dialog]', vez=2); t = toast()
    chk('A15c 390 px: erro (100 ha) junto ao campo; aceite com clique duplo registra um contrato', 'não pode ficar abaixo' in a and ('Aceite registrado' in t or 'Aceite já registrado' in t) and J("JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).assin.orgs.sr.contratos.length") == 3, [a, t])
    clk('Fechar', 'aside[role=dialog]'); data('01/10/2026'); clk('Pagar fatura'); clk('Cartão final 4242 · simulado', 'aside[role=dialog]'); clk('Confirmar pagamento (simulado)', 'aside[role=dialog]', vez=2); t = toast()
    npg = J("JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).assin.orgs.sr.faturas.find(f=>f.comp==='2026-09').eventos.filter(e=>/^Paga/.test(e.t)).length")
    c.shot(os.path.join(PROBE, 'assin_cf05_390_paga.png'))
    chk('A15d 390 px: Pagar fatura → cartão simulado → clique duplo paga uma vez (mesmo recibo)', ('Pagamento simulado confirmado' in t or 'Pagamento já registrado · recibo PAG-0001' in t) and npg == 1, [t, npg])
    # revisão PLAT, achado 12: no celular a faixa mostra só o essencial (antes ocupava 123 px do cabeçalho)
    go('CF-05.dc.html', limpa=True); data('16/10/2026'); go('OS.dc.html')
    fx390 = J("(()=>{const f=document.querySelector('header [aria-label=Cobrança]'); if(!f) return null; const r=f.getBoundingClientRect(); return {h:Math.round(r.height),t:f.innerText.replace(/\\s+/g,' '),w:Math.round(r.width),vw:innerWidth};})()")
    c.shot(os.path.join(PROBE, 'assin_faixa_390.png'))
    chk('A15e 390 px: faixa vermelha curta (≤ 60 px de altura): fatura vencida, o que está suspenso e o link Pagar fatura; sem rolagem lateral',
        fx390 and fx390['h'] <= 60 and 'vencida há 15 dias · talhão novo suspenso' in fx390['t'] and 'Pagar fatura' in fx390['t'] and 'nada foi apagado' not in fx390['t'] and fx390['w'] <= fx390['vw'], fx390)
    ERRL.extend(errs())
    chk('A0 sem erro de JavaScript nas telas visitadas', not ERRL, ERRL[:6])
finally:
    if c: c.close()
    srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FA)} falhas'); [print('  -', f) for f in FA]
sys.exit(1 if FA else 0)
