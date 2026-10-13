# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO (5983172395) no Estoque na forma do SUP (docs/suprimentos-simplificado §3 e §9.3): 4 seções e os modos
Movimentos e Produção de Confira saldos. Fica a regra: uma variável por coluna (até 7 de dado), a quantidade leva a unidade junto ("60.000 kg",
decisão do proprietário de 05/10/2026) e ordena pelo número; filtro por valor exato; página sem rolagem horizontal; identificação à vista a 390 px.
Mudou o mapa de colunas (eram 6 seções com até 12 colunas) e a navegação (seção pelo nome).
Só as colunas essenciais (pedido do proprietário de 10/10/2026): identificação, situação, quem retira ou devolve e os números que decidem; o que saiu
(lote da requisição, fornecedor, contado, reservado, bloqueado, lote do movimento) aparece no painel do registro e o que servia para achar segue na busca.
Uso: python3 tabelas_est_test.py [pasta de capturas]"""
import sys, os, time, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
OUT = sys.argv[1] if len(sys.argv) > 1 else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''))

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
TB = "[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent)"
def heads(): return [x.upper() for x in (J(f"[...({TB}).querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().replace(/ · \\d+$/,''))") or [])]
def linhas(): return J(f"[...({TB}).querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.replace(/\\s+/g,' ').replace(/^[▸▾]\\s*/,'').trim()))") or []
def dicts(): hs = heads(); return [dict(zip(hs, r)) for r in linhas()]
def secao(nome): J(f"[...document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')].find(b=>(b.querySelector('span')||b).innerText.trim()==={json.dumps(nome)}).click()"); time.sleep(.5)
def modo(nome): J(f"[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&b.innerText.trim()==={json.dumps(nome)}).click()"); time.sleep(.5)
def filtra(col, vals):
    J(f"({TB}).querySelector('button[aria-label=\"Filtrar {col}\"]').click()"); time.sleep(.4)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Limpar').click()"); time.sleep(.2)
    for v in vals: J(f"(()=>{{const l=[...document.querySelectorAll('[role=dialog] label')].find(l=>l.innerText.replace(/\\s+\\d+$/,'').trim()==={json.dumps(v)}); l&&l.querySelector('input').click();}})()"); time.sleep(.15)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='OK').click()"); time.sleep(.5)
def limpa(): J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&/^Limpar filtros/.test(b.innerText.trim())); b&&b.click();})()"); time.sleep(.4)
def ordena(col, desc=False):
    J(f"({TB}).querySelector('button[aria-label=\"Filtrar {col}\"]').click()"); time.sleep(.4)
    J(f"[...document.querySelectorAll('[role=dialog] button.g2fi')][{1 if desc else 0}].click()"); time.sleep(.5)
def num(t): return float(t.replace('.', '').replace(',', '.').replace('−', '-').replace('+', ''))
NUMRE = r'^[+−-]?[\d.]+(,\d+)?$'
QRE = r'^[+−-]?[\d.]+(,\d+)? (kg|L|un|sc|t|g|mL)$'   # quantidade com a unidade junto
def shot(n):
    if OUT: c.shot(os.path.join(OUT, n + '.png'))
def cab_visiveis():
    return J(f"(()=>{{const t={TB}; const sc=t.parentElement; sc.scrollLeft=0; const R=sc.getBoundingClientRect(); return [...t.querySelectorAll('[role=columnheader]')].filter(h=>h.getBoundingClientRect().right<=R.right+0.5).map(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().replace(/ · \\d+$/,'').toUpperCase());}})()") or []

VISOES = [('Atenda requisições', None, ('REQUISIÇÃO › ITEM', 'SITUAÇÃO', 'A ENTREGAR', 'EM CUSTÓDIA', 'COM QUEM', 'O.S.'), 'REQUISIÇÃO › ITEM'),
          ('Receba e inspecione', None, ('DOCUMENTO › ITEM', 'SITUAÇÃO', 'NA NOTA', 'EM QUARENTENA', 'PREVISÃO'), 'DOCUMENTO › ITEM'),
          ('Faça contagens', None, ('CONTAGEM', 'SITUAÇÃO', 'ITEM', 'LOTE', 'LOCAL', 'DIFERENÇA'), 'CONTAGEM'),
          ('Confira saldos', 'Lotes', ('ITEM', 'LOTE', 'FÍSICO', 'DISPONÍVEL', 'VALIDADE'), 'ITEM'),
          ('Confira saldos', 'Movimentos', ('DATA E HORA', 'MOVIMENTO', 'DOCUMENTO', 'ITEM', 'QUANTIDADE', 'QUEM'), 'DATA E HORA')]
PAINEL = "(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); return a?a.innerText.replace(/\\s+/g,' '):'';})()"
def painel(txt):
    J(f"(()=>{{const r=[...({TB}).querySelectorAll('[role=row]')].find(x=>x.offsetParent&&x.innerText.indexOf({json.dumps(txt)})>=0); r&&(r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.6)
    t = J(PAINEL) or ''; J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.offsetParent&&/^(Fechar|Cancelar)$/.test(b.innerText.trim())); b&&b.click(); document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));})()"); time.sleep(.4); return t
def busca(q):
    J(f"(()=>{{const i=[...document.querySelectorAll('input[aria-label=\"Buscar nesta tabela\"]')].find(x=>x.offsetParent); if(!i) return; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(q)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.5)
    return [r[0] for r in linhas()]
QTD = {'A ENTREGAR', 'EM CUSTÓDIA', 'NA NOTA', 'EM QUARENTENA', 'DIFERENÇA', 'FÍSICO', 'DISPONÍVEL', 'QUANTIDADE'}

try:
    c.aparelho(1440, 900, 1, False)
    c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(f'http://127.0.0.1:{p}/EST.dc.html', 1.6); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    # trilha com movimentos de vários itens: OS-0430 liberada, 3 itens entregues e confirmados no app, turno de 5 ha fechado
    J("""(()=>{const X=window.__cen; with(X){ cenMudar(null,c=>cenLiberar(c,'OS-0430')); const c0=cenGet(); const rq=Object.keys(c0.reqs).find(k=>c0.reqs[k].os==='OS-0430');
      cenMudar(null,c=>cenEntregar(c,rq,'Glifosato 480',320,'Marcos','Rui')); cenMudar(null,c=>cenEntregar(c,rq,'2,4-D 806',160,'Marcos','Rui')); cenMudar(null,c=>cenEntregar(c,rq,'Óleo mineral',80,'Marcos','Rui'));
      cenMudar(null,c=>cenConfirmarRecebimento(c,rq)); cenMudar(null,c=>cenIniciarTurno(c,'OS-0430')); return cenMudar(null,c=>cenFecharTurno(c,5,1)).erro||''; } })()""")
    c.goto(f'http://127.0.0.1:{p}/EST.dc.html', 1.4); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    J("[...document.querySelectorAll('select[aria-label=\"Filtrar por fazenda\"]')].forEach(i=>{Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,'Todas'); i.dispatchEvent(new Event('change',{bubbles:true}));})"); time.sleep(.5)
    for i, (sec, md, esperado, ident) in enumerate(VISOES, 1):
        secao(sec)
        if md: modo(md)
        for _ in range(2): J(f"[...({TB}).querySelectorAll('button[aria-label^=\"Expandir\"]')].filter(b=>b.offsetParent).forEach(b=>b.click())"); time.sleep(.3)
        hs = heads(); d = dicts(); nome = sec + (' › ' + md if md else ''); shot(f'est{i}-1440')
        chk(f'{nome}: só as colunas essenciais ({", ".join(esperado)}); sem coluna Unidade', tuple(hs) == esperado and 'UNIDADE' not in hs and len(hs) <= 7, hs)
        semun = [(h, v) for r in d for h, v in r.items() if h in QTD and v not in ('', '—', '0') and re.match(NUMRE, v.split(' ')[0]) and not re.match(QRE, ' '.join(v.split(' ')[:2]))]
        chk(f'{nome}: cada quantidade com a unidade junto ("60.000 kg")', not semun, semun[:3])
        chk(f'{nome}: página sem rolagem horizontal; identificação ({ident}) à vista sem rolar a grade', J("document.documentElement.scrollWidth<=innerWidth+1") and ident in cab_visiveis(), cab_visiveis()[:4])
        if sec == 'Atenda requisições':
            sits = sorted({r.get('SITUAÇÃO') for r in d if r.get('SITUAÇÃO')}); filtra('Situação', [sits[0]] if sits else []); r1 = dicts()
            chk('requisições: filtro Situação por valor exato', len(sits) > 1 and r1 and len({r.get('SITUAÇÃO') for r in r1}) == 1, (sits, len(r1)))
            limpa(); os_ = [r.get('O.S.') for r in dicts() if r.get('O.S.')]
            chk('requisições: O.S. em coluna própria (OS-… ou a ordem de beneficiamento OB-…, BEN-D05), separada da requisição', os_ and all(re.match(r'^(OS|OB)-', o) for o in os_), os_[:3])
            pn = painel('REQ-039'); bq = busca('F26-02'); busca('')
            chk('requisições: o lote saiu da grade e está no painel (REQ-039 › Fungicida A, lote F26-02) e na busca ("F26-02" acha a REQ-039)',
                'Fungicida A (lote F26-02)' in pn and any(x.startswith('REQ-039') for x in bq), [pn[:160], bq[:4]])
        if sec == 'Receba e inspecione':
            # integração BEN, rodada 1 (BEN-D23): a NF 7731 das caixas do packing (PC-096, a conferir) entra na lista com a unidade do pedido (un, não kg)
            n77 = next((r for r in d if (r.get('DOCUMENTO › ITEM') or '').startswith('NF 7731')), {})
            chk('notas: NF 7731 (caixas, PC-096) a conferir, 1.200 un na nota (unidade do pedido)', n77.get('SITUAÇÃO') == 'A conferir' and n77.get('NA NOTA') == '1.200 un', n77)
            n33 = next((r for r in d if (r.get('DOCUMENTO › ITEM') or '').startswith('NF 4533')), {}).get('DOCUMENTO › ITEM', '')
            k11 = next((r for r in d if 'K26-11' in (r.get('DOCUMENTO › ITEM') or '')), {}).get('DOCUMENTO › ITEM', '')
            chk('notas: a célula do documento diz o item (sem coluna Item repetida): "NF 4533 › Semente de soja…" e a parcela "NF 4501 › KCl 60% · K26-11"',
                n33.startswith('NF 4533 › Semente de soja') and k11.startswith('NF 4501 › KCl 60% · K26-11'), [n33, k11])
            pn = painel('NF 4533'); bq = busca('Coop'); busca('')
            chk('notas: o fornecedor saiu da grade e está no painel da nota (PC-090 · Coop. …) e na busca', 'PC-090 · Coop' in pn and any(x.startswith('NF 4533') for x in bq), [pn[:160], bq[:4]])
        if sec == 'Confira saldos' and md == 'Lotes':
            kcl = next((r for r in d if r.get('LOTE') == 'K26-11'), {}); pn = painel('K26-11')
            chk('lotes: K26-11 (KCl 60%, selo "Em quarentena" na linha: o estado não sai da vista) físico 60.000 kg, disponível 50.000 kg; uma linha por lote (sem árvore); o bloqueado (10.000 kg) e a conta no painel',
                [kcl.get(k) for k in ('ITEM', 'FÍSICO', 'DISPONÍVEL')] == ['KCl 60% Em quarentena', '60.000 kg', '50.000 kg'] and 'Disponível = físico − reservado − bloqueado = 60.000 kg − 0 kg − 10.000 kg = 50.000 kg' in pn, [kcl, pn[:200]])
            sem = [r.get('LOTE') for r in d if 'Em quarentena' in (r.get('ITEM') or '')]
            chk('lotes: o selo "Em quarentena" só nos lotes com parcela bloqueada (K26-11 na semente)', sem == ['K26-11'], sem)
            ordena('Disponível', desc=True); v4 = [num(r['DISPONÍVEL'].split(' ')[0]) for r in dicts() if re.match(NUMRE, r.get('DISPONÍVEL', '').split(' ')[0])]
            chk('lotes: ordenar Disponível decrescente pelo número (a unidade junto não atrapalha)', len(v4) > 1 and v4 == sorted(v4, reverse=True), v4[:6])
            limpa(); ordena('Validade'); vs = [r.get('VALIDADE') for r in dicts() if re.match(r'^\d{2}/\d{4}$', r.get('VALIDADE', ''))]
            ym = [int(v[3:]) * 100 + int(v[:2]) for v in vs]
            chk('lotes: ordenar Validade pela data (mês/ano), não pelo texto', len(ym) > 1 and ym == sorted(ym), vs[:6])
            limpa()
        if md == 'Movimentos':
            movs6 = sorted({r.get('MOVIMENTO') for r in d}); filtra('Movimento', [movs6[0]] if movs6 else []); r6 = dicts()
            chk('movimentos: filtro Movimento por valor exato', len(movs6) > 1 and r6 and len({r.get('MOVIMENTO') for r in r6}) == 1, (movs6, len(r6)))
            limpa(); res6 = [r for r in dicts() if r.get('MOVIMENTO') == 'Reserva']
            chk('movimentos: reserva com quantidade "320 L" (unidade junto)', res6 and all(re.match(QRE, r.get('QUANTIDADE', '')) for r in res6), [r.get('QUANTIDADE') for r in res6][:3])
    # Produção (Colheita integrada, c.producao): resumo do físico na unidade da cultura e atalho à página da Colheita; não é grade copiada
    secao('Confira saldos'); modo('Produção'); tp = J("document.querySelector('main').innerText")
    chk('Produção: Santa Rita com "Soja em grão 38.420 sc" lido da Colheita e atalho "Abrir Estoque de produto ›" (PROD.dc.html)',
        'Soja em grão' in tp and '38.420 sc' in tp and J("[...document.querySelectorAll('main a')].some(a=>a.getAttribute('href')==='PROD.dc.html'&&/Abrir Estoque de produto/.test(a.innerText))"), tp[-400:])
    modo('Lotes')
    # 390 px: em cada seção a página não rola e a identificação fica à vista
    c.aparelho(390, 844, 2, True); c.goto(f'http://127.0.0.1:{p}/EST.dc.html', 1.4); r390 = []
    for sec, md, esperado, ident in VISOES:
        secao(sec)
        if md: modo(md)
        r390.append((sec + (md or ''), bool(J("document.documentElement.scrollWidth<=innerWidth+1")), ident in cab_visiveis()))
    shot('est4-390')
    chk('390 px: as 4 seções e Movimentos sem rolagem da página e com a identificação à vista', all(a and b for _, a, b in r390), r390)
    chk('sem erro de script', not J("window.__e"), J("window.__e"))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
