# -*- coding: utf-8 -*-
"""PLAT-01 · teste de navegador da plataforma (backoffice): BO-02 Assinaturas e cobrança e BO-01 Planos e preços (ESPECIFICACAO.md §8: A11, A12,
A13, A14, A15 nas telas da plataforma). BO-02: totais da §6 lidos do mesmo estado (vigentes R$ 6.278,46 · 2 faturas abertas R$ 939,00 · área
cobrada 2.945,23 ha), uma primária, detalhe sem talhão/cultura/safra, conciliar uma vez (normal), conciliar de novo sem duplicar (repetição),
pagamento feito no CF-05 aparece Paga no BO-02. Revisão PLAT (06/10): conciliação com a chave de quem inicia e primária desabilitada quando nada resta (A12d/e), primária Resolver
contestação (A12i), quem age nos eventos (A12e/f), dia do trial igual no ON-01 e no BO-02 (A12j), simulação a partir da área medida (A12g2).
BO-01: parâmetros com o selo "a decidir pelo proprietário", simulação 20…5.000 ha calculada no
navegador, simular acima de 5.000 ha recusado (erro). Desktop 1440 × 900 e celular 390 × 844.
Uso (de gen37/, depois de build.py e montar_render.py): python3 plataforma_test.py"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, MEDE
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
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def dlg(): return J(f"(()=>{{const d=[...document.querySelectorAll('aside[role=dialog]')].find({VIS}); return d?d.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def clk(t, root='', vez=1):
    r = J(f"""(()=>{{const n={N}, vis={VIS}; const R=[...document.querySelectorAll({json.dumps(root or 'body')})].filter(vis).pop()||document.body;
      const es=[...R.querySelectorAll('button,a')].filter(e=>vis(e)&&!e.disabled); const e=es.find(x=>n(x.innerText)===n({json.dumps(t)}))||es.find(x=>n(x.innerText).startsWith(n({json.dumps(t)})));
      if(!e) return 'sem '+{json.dumps(t)}; for(let i=0;i<{vez};i++) e.click(); return 'ok';}})()""")
    time.sleep(.5); return r
def setv(sel, val):
    J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); if(!i) return 0; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(val)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}})); return 1;}})()"""); time.sleep(.3)
def tabela(i): return J(f"(()=>{{const t=document.querySelectorAll('main [role=table]')[{i}]; return t?t.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def linha(i, txt): return J(f"(()=>{{const t=document.querySelectorAll('main [role=table]')[{i}]; const r=t&&[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()") or ''
def abre_linha(i, txt):
    r = J(f"(()=>{{const t=document.querySelectorAll('main [role=table]')[{i}]; const r=t&&[...t.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf({json.dumps(txt)})>=0); if(!r) return 'sem linha'; (r.querySelector('[role=cell]')||r).click(); return 'ok';}})()")
    time.sleep(.5); return r
def selo(): return J("(()=>{const h=document.querySelector('header h1'); const s=h&&h.nextElementSibling; return s?s.innerText.trim():'';})()") or ''
GRADES = """(()=>[...document.querySelectorAll('main .g2caixa')].map(x=>({busca:!!x.querySelector('input[type=search]'),ord:x.querySelectorAll('.g2hb').length,fil:x.querySelectorAll('.g2fb').length})))()"""
try:
    c = Chrome(); c.aparelho(1440, 900)
    # ============ BO-02 ============
    go('BO-02.dc.html', limpa=True); b = body()
    chk('A12a BO-02 em 23/09: mensalidades vigentes R$ 6.278,46 · 2 faturas abertas R$ 939,00 · área cobrada 2.945,23 ha (medida 2.958,23 ha)',
        all(x in b for x in ('R$ 6.278,46', '2 · R$ 939,00', '2.945,23 ha', 'medida 2.958,23 ha')), b[:700])
    chk('A12b organizações por estado: Ativa 3 · Inadimplente 1 · Em avaliação 1 · Cancelada 1; selo "2 eventos a conciliar"',
        'Ativa 3 · Inadimplente 1 · Em avaliação 1 · Cancelada 1' in b and selo() == '2 eventos a conciliar', [selo(), b[:500]])
    chk('A11a BO-02: uma primária (Conciliar pagamentos)', J(PRIMS) == ['Conciliar pagamentos'], J(PRIMS))
    g = J(GRADES); chk('A14a BO-02: as 2 grades têm busca, ordenação e filtro por coluna; R$ e ha na célula', len(g) == 2 and all(x['busca'] and x['ord'] >= 5 and x['fil'] >= 5 for x in g)
        and 'R$ 5.140,46' in linha(0, 'Grupo Santa Rita') and '2.570,23 ha' in linha(0, 'Grupo Santa Rita') and '2.600 ha' in linha(0, 'Grupo Santa Rita'), [g, linha(0, 'Grupo Santa Rita')])
    chk('A12c linhas do seed: Aurora inadimplente (ago/2026 vencida, 3 tentativas), Bela Vista com evento a conciliar, Boa Esperança em avaliação (dia 5 de 30), Dois Rios cancelada',
        'Inadimplente' in linha(0, 'Fazenda Aurora') and '3 tentativas recusadas' in linha(0, 'Fazenda Aurora') and 'evento do provedor a conciliar' in linha(0, 'Agro Bela Vista')
        and 'dia 5 de 30' in linha(0, 'Boa Esperança') and 'consulta e exportação até 29/11/2026' in linha(0, 'Dois Rios'), [linha(0, 'Fazenda Aurora'), linha(0, 'Agro Bela Vista')])
    abre_linha(0, 'Grupo Santa Rita'); d = dlg()
    chk('A13 detalhe da organização: área por fazenda e faturas; nenhum talhão, cultura ou safra; link de consulta contratual ao CF-05',
        all(x in d for x in ('Santa Rita', 'Lagoa Grande', 'Boa Vista', '1.285,23 ha', 'ago/2026 · R$ 2.330,00')) and not any(x in d for x in ('PV01', 'T1 ', 'Soja', 'Milho', 'Mamão', '2026/27'))
        and J("!![...document.querySelectorAll('aside[role=dialog] a')].find(a=>a.getAttribute('href')==='CF-05.dc.html')"), d[:900])
    clk('Fechar', 'aside[role=dialog]')
    clk('Conciliar pagamentos', vez=2); t1 = toast(); b = body()
    ncon = J("Object.values(JSON.parse(localStorage.getItem('talhao-os-cenario-v1')).assin.recibos).filter(r=>/^CON-/.test(r.id)).length")
    chk('A12d conciliar (clique duplo, mesma chave): um recibo CON-0001; Bela Vista paga (evt_1JKT5) e a recusa da Aurora registrada; 1 fatura aberta R$ 299,00',
        ('Conciliado (CON-0001): 1 pagamento aprovado · 1 recusa registrada' in t1 or 'Conciliação já registrada (CON-0001)' in t1) and ncon == 1
        and '1 · R$ 299,00' in b and 'Conciliado' in linha(1, 'evt_1JKT5') and selo() == 'Pagamentos conciliados', [t1, ncon, b[:400]])
    # revisão PLAT, achado 9: sem evento a conciliar nem contestação, a primária fica desabilitada com o motivo (antes respondia "nada mudou")
    pb = J("(()=>{const b=[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos'); return b?{dis:b.getAttribute('aria-disabled')==='true',tit:b.title}:null;})()")   # DS-DICA-20261009: aria-disabled (focável, com dica)
    abre_linha(0, 'Fazenda Aurora'); d = dlg()
    chk('A12e tudo conciliado: primária Conciliar pagamentos desabilitada com o motivo; a recusa aparece uma vez na Aurora, com quem conciliou',
        pb and pb['dis'] is True and 'Nenhum evento do provedor a conciliar' in pb['tit'] and d.count('evt_1JKR9') == 1 and 'Vencida' in d and 'por Admin plataforma' in d, [pb, d[:600]])
    clk('Fechar', 'aside[role=dialog]')
    # pagar no CF-05 aparece Paga no BO-02 (mesmo estado)
    go('CF-05.dc.html'); clk('01/10/2026'); clk('Pagar fatura'); clk('Boleto · simulado', 'aside[role=dialog]'); clk('Confirmar pagamento (simulado)', 'aside[role=dialog]')
    go('BO-02.dc.html'); abre_linha(0, 'Grupo Santa Rita'); d = dlg()
    chk('A12f pagamento feito no CF-05 aparece Paga no BO-02 (set/2026, R$ 5.140,46), com quem pagou e quem aceitou o contrato', 'set/2026 · R$ 5.140,46' in d and 'Paga · evt_sim_0001 · Boleto' in d
        and 'recibo PAG-0001 · por Ana · Gestora' in d and 'aceite 28/08 por Ana · Gestora' in d, d[:900])
    clk('Fechar', 'aside[role=dialog]')
    # contestação pendente sem evento a conciliar: a primária leva à contestação; resolver volta a primária desabilitada (achado 9)
    go('BO-02.dc.html', limpa=True); clk('Conciliar pagamentos'); go('CF-05.dc.html'); clk('01/10/2026'); abre_linha(1, 'set/2026'); clk('Contestar fatura', 'aside[role=dialog]')
    J("(()=>{const i=document.querySelector('#cf_motivo'); Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(i,'Área da Lagoa contada antes do aceite'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 1;})()")
    time.sleep(.3); clk('Registrar contestação', 'aside[role=dialog]'); clk('Fechar', 'aside[role=dialog]')
    go('BO-02.dc.html'); p0 = J(PRIMS); clk('Resolver contestação'); d = dlg()
    clk('Manter o valor', 'aside[role=dialog]'); clk('Registrar resolução', 'aside[role=dialog]'); t = toast(); clk('Fechar', 'aside[role=dialog]')
    pb = J("(()=>{const b=[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Conciliar pagamentos'); return b?b.getAttribute('aria-disabled')==='true':null;})()")   # DS-DICA-20261009
    chk('A12i contestação aberta e nada a conciliar: primária Resolver contestação abre a Santa Rita; Registrar resolução (manter) volta a primária desabilitada',
        p0 == ['Resolver contestação'] and 'Grupo Santa Rita' in d and 'Contestação de set/2026' in d and 'resolvida (RES-0001): valor mantido' in t and pb is True, [p0, d[:300], t, pb])
    # dia do trial pela mesma data simulada no ON-01 e no BO-02 (achado 8)
    go('ON-01.dc.html'); on16 = J("document.querySelector('main').innerText.replace(/\\s+/g,' ')") or ''; go('BO-02.dc.html'); bo16 = linha(0, 'Boa Esperança')
    chk('A12j trial da Boa Esperança em 01/10: ON-01 e BO-02 dizem "dia 13 de 30" (mesma data simulada, nada fixo)', 'dia 13 de 30' in on16 and 'dia 13 de 30' in bo16, [on16[:300], bo16])
    # ============ BO-01 ============
    go('BO-01.dc.html'); b = body()
    chk('A11b BO-01: uma primária (Simular área); telas irmãs Assinaturas e cobrança · Planos e preços', J(PRIMS) == ['Simular área'] and J("[...document.querySelectorAll('nav.etp a')].map(a=>a.innerText.trim()).join('|')") == 'Assinaturas e cobrança|Planos e preços', [J(PRIMS)])
    chk('A14b BO-01: parâmetros (Avaliação, Essencial, Completo) com "a decidir pelo proprietário"; R$ 24,00/ha·ano no Completo',
        all(x in tabela(0) for x in ('Avaliação', 'Essencial', 'Completo', 'R$ 24,00/ha·ano', 'a decidir pelo proprietário')), tabela(0)[:500])
    sim = {h: linha(1, h) for h in ('20 ha', '149,5 ha', '500 ha', '1.000 ha', '5.000 ha')}
    chk('A14c simulação calculada no navegador: 20 ha 199/299 (mínimo) · 149,5 ha 224,25 · 500 ha 750/1.000 · 1.000 ha 1.500/2.000 · 5.000 ha 7.500/10.000',
        'R$ 199,00' in sim['20 ha'] and 'R$ 299,00' in sim['20 ha'] and 'R$ 224,25' in sim['149,5 ha'] and 'R$ 750,00' in sim['500 ha'] and 'R$ 1.000,00' in sim['500 ha']
        and 'R$ 1.500,00' in sim['1.000 ha'] and 'R$ 2.000,00' in sim['1.000 ha'] and 'R$ 7.500,00' in sim['5.000 ha'] and 'R$ 10.000,00' in sim['5.000 ha'], sim)
    g = J(GRADES); chk('A14d BO-01: as 2 grades têm busca, ordenação e filtro', len(g) == 2 and all(x['busca'] and x['ord'] >= 3 for x in g), g)
    clk('Simular área'); d = dlg(); sha = J("document.querySelector('#bo_sha').value")
    chk('A12g Simular área começa na área medida (2.570,23 ha): Essencial R$ 3.855,35 e Completo R$ 5.140,46 por mês', sha == '2.570,23' and 'R$ 3.855,35/mês' in d and 'R$ 5.140,46/mês' in d, [sha, d[:400]])
    clk('Fechar', 'aside[role=dialog]')
    J('localStorage.setItem("talhao-os-cd01-v1", ' + json.dumps(json.dumps(cad_mais({'id':'TN01','v':{'t':'T9','faz':'Santa Rita','decl':50,'sit':'Ativo'}}))) + '); 1')
    go('BO-01.dc.html'); clk('Simular área'); d = dlg(); sha = J("document.querySelector('#bo_sha').value"); J("localStorage.removeItem('talhao-os-cd01-v1'); 1")
    chk('A12g2 com um talhão de 50 ha no cadastro a simulação começa em 2.620,23 ha (lida do cadastro, revisão PLAT achado 8)', sha == '2.620,23' and 'R$ 5.240,46/mês' in d, [sha, d[:300]])
    setv('#bo_sha', '9.000'); d = dlg()
    chk('A12h Simular acima de 5.000 ha: recusa com "proposta empresarial, a decidir pelo proprietário"', 'Acima de 5.000 ha: proposta empresarial' in d and '/mês' not in d, d[:300])
    clk('Fechar', 'aside[role=dialog]')
    # ============ celular 390 px ============
    c.aparelho(390, 844, 2, True); go('BO-02.dc.html'); md = J(MEDE); c.shot(os.path.join(PROBE, 'assin_bo02_390.png'))
    chk('A15 390 px BO-02: sem rolagem lateral da página, primária alcançável, resumo 2 × 2', not md.get('pagLado') and md.get('prim') == ['Conciliar pagamentos'] and not md.get('primRuim')
        and J("getComputedStyle(document.querySelector('.assin-kpis')).gridTemplateColumns.split(' ').length") == 2, md)
    abre_linha(0, 'Fazenda Aurora'); md = J(MEDE)
    chk('A15b 390 px BO-02: detalhe da organização dentro da tela, com fechar alcançável', md.get('painel') and not md.get('painelFora') and md.get('painelFechar'), md)
    go('BO-01.dc.html'); md = J(MEDE); c.shot(os.path.join(PROBE, 'assin_bo01_390.png'))
    chk('A15c 390 px BO-01: sem rolagem lateral, primária alcançável', not md.get('pagLado') and md.get('prim') == ['Simular área'] and not md.get('primRuim'), md)
    ERRL.extend(errs())
    chk('A0 sem erro de JavaScript nas telas visitadas', not ERRL, ERRL[:6])
finally:
    if c: c.close()
    srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FA)} falhas'); [print('  -', f) for f in FA]
sys.exit(1 if FA else 0)
