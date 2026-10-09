# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO (5983172395) no Estoque na forma do SUP (docs/suprimentos-simplificado §3 e §9.3): 4 seções e os modos
Movimentos e Produção de Confira saldos. Fica a regra: uma variável por coluna (até 7 de dado), a quantidade leva a unidade junto ("60.000 kg",
decisão do proprietário de 05/10/2026) e ordena pelo número; filtro por valor exato; página sem rolagem horizontal; identificação à vista a 390 px.
Mudou o mapa de colunas (eram 6 seções com até 12 colunas) e a navegação (seção pelo nome).
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

VISOES = [('Atenda requisições', None, ('REQUISIÇÃO › ITEM', 'SITUAÇÃO', 'A ENTREGAR', 'EM CUSTÓDIA', 'COM QUEM', 'O.S.', 'LOTE'), 'REQUISIÇÃO › ITEM'),
          ('Receba e inspecione', None, ('DOCUMENTO › ITEM', 'SITUAÇÃO', 'ITEM', 'NA NOTA', 'EM QUARENTENA', 'PREVISÃO', 'FORNECEDOR'), 'DOCUMENTO › ITEM'),
          ('Faça contagens', None, ('CONTAGEM', 'SITUAÇÃO', 'ITEM', 'LOTE', 'LOCAL', 'CONTADO', 'DIFERENÇA'), 'CONTAGEM'),
          ('Confira saldos', 'Lotes', ('ITEM', 'LOTE', 'FÍSICO', 'RESERVADO', 'BLOQUEADO', 'DISPONÍVEL', 'VALIDADE'), 'ITEM'),
          ('Confira saldos', 'Movimentos', ('DATA E HORA', 'MOVIMENTO', 'DOCUMENTO', 'ITEM', 'LOTE', 'QUANTIDADE', 'QUEM'), 'DATA E HORA')]
QTD = {'A ENTREGAR', 'EM CUSTÓDIA', 'NA NOTA', 'EM QUARENTENA', 'CONTADO', 'DIFERENÇA', 'FÍSICO', 'RESERVADO', 'BLOQUEADO', 'DISPONÍVEL', 'QUANTIDADE'}

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
        chk(f'{nome}: colunas {", ".join(esperado[:3])}…; até 7 de dado; sem coluna Unidade', tuple(hs) == esperado and 'UNIDADE' not in hs and len(hs) <= 7, hs)
        semun = [(h, v) for r in d for h, v in r.items() if h in QTD and v not in ('', '—', '0') and re.match(NUMRE, v.split(' ')[0]) and not re.match(QRE, ' '.join(v.split(' ')[:2]))]
        chk(f'{nome}: cada quantidade com a unidade junto ("60.000 kg")', not semun, semun[:3])
        chk(f'{nome}: página sem rolagem horizontal; identificação ({ident}) à vista sem rolar a grade', J("document.documentElement.scrollWidth<=innerWidth+1") and ident in cab_visiveis(), cab_visiveis()[:4])
        if sec == 'Atenda requisições':
            sits = sorted({r.get('SITUAÇÃO') for r in d if r.get('SITUAÇÃO')}); filtra('Situação', [sits[0]] if sits else []); r1 = dicts()
            chk('requisições: filtro Situação por valor exato', len(sits) > 1 and r1 and len({r.get('SITUAÇÃO') for r in r1}) == 1, (sits, len(r1)))
            limpa(); os_ = [r.get('O.S.') for r in dicts() if r.get('O.S.')]
            chk('requisições: O.S. em coluna própria (OS-…), separada da requisição', os_ and all(o.startswith('OS-') for o in os_), os_[:3])
        if sec == 'Confira saldos' and md == 'Lotes':
            kcl = next((r for r in d if r.get('LOTE') == 'K26-11'), {})
            chk('lotes: K26-11 (KCl 60%) físico 60.000 kg, bloqueado 10.000 kg, disponível 50.000 kg; uma linha por lote (sem árvore)',
                [kcl.get(k) for k in ('ITEM', 'FÍSICO', 'BLOQUEADO', 'DISPONÍVEL')] == ['KCl 60%', '60.000 kg', '10.000 kg', '50.000 kg'], kcl)
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
    # Produção (Colheita): vazio na semente, com o texto do que vem
    secao('Confira saldos'); modo('Produção')
    chk('Produção: sem lote na semente, diz de onde vem', 'A Colheita registra aqui' in J("document.querySelector('main').innerText"))
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
