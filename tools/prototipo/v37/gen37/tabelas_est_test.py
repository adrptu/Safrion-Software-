# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), incremento 2c: Estoque (EST.dc.html), uma variável por coluna nas 6 seções.
TF03: item, lote, requisição, O.S., nota, data, pedido, fornecedor, situação e detalhe em colunas próprias; a quantidade leva a unidade junto
("60.000 kg", decisão do proprietário de 05/10/2026: mais intuitivo, filtrar unidade não gera valor) e ordena pelo número; filtro por valor
exato; árvore item › lote preservada; página sem rolagem horizontal.
Uso: python3 tabelas_est_test.py [pasta de capturas]   (< 90 s)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, cv_todas_sempre
OUT = sys.argv[1] if len(sys.argv) > 1 else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''))

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js; cv_todas_sempre(c)   # V2-3: a tabela completa como foi desenhada (TABELAS-FOCO); o padrão é conferido na VISOES-2
TB = "[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent)"
def heads(): return [x.upper() for x in (J(f"[...({TB}).querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().replace(/ · \\d+$/,''))") or [])]
def linhas(): return J(f"[...({TB}).querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.replace(/\\s+/g,' ').replace(/^[▸▾]\\s*/,'').trim()))") or []
def dicts(): hs = heads(); return [dict(zip(hs, r)) for r in linhas()]
def secao(i): J(f"document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[{i - 1}].click()"); time.sleep(.5)
def filtra(col, vals):
    J(f"({TB}).querySelector('button[aria-label=\"Filtrar {col}\"]').click()"); time.sleep(.4)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Limpar').click()"); time.sleep(.2)
    for v in vals: J(f"(()=>{{const l=[...document.querySelectorAll('[role=dialog] label')].find(l=>l.innerText.replace(/\\s+\\d+$/,'').trim()==={json.dumps(v)}); l&&l.querySelector('input').click();}})()"); time.sleep(.15)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='OK').click()"); time.sleep(.5)
def limpa(): J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&/^Limpar filtros/.test(b.innerText.trim())); b&&b.click();})()"); time.sleep(.4)
def ordena(col, desc=False):
    J(f"({TB}).querySelector('button[aria-label=\"Filtrar {col}\"]').click()"); time.sleep(.4)
    J(f"[...document.querySelectorAll('[role=dialog] button.g2fi')][{1 if desc else 0}].click()"); time.sleep(.5)
def num(t): return float(t.replace('.', '').replace(',', '.').replace('−', '-'))
NUMRE = r'^[+−-]?[\d.]+(,\d+)?$'
import re
def shot(n):
    if OUT: c.shot(os.path.join(OUT, n + '.png'))

try:
    c.aparelho(1440, 900, 1, False)
    c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(f'http://127.0.0.1:{p}/EST.dc.html', 1.6); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    QTD = {'NA NOTA', 'CONFERIDA', 'APTA', 'QUARENTENA', 'SOLICITADO', 'ENTREGUE', 'A ENTREGAR', 'CONSUMIDO', 'DEVOLVIDO', 'EM CUSTÓDIA', 'FÍSICO', 'RESERVADO', 'BLOQUEADO',
           'DISPONÍVEL', 'EM CONFERÊNCIA', 'EM CUSTÓDIA (FORA DO DEPÓSITO)', 'SISTEMA NA DATA DE CORTE', 'CONTADO', 'DIFERENÇA', 'QUANTIDADE'}
    esperado = {1: ('NOTA FISCAL', 'DATA DA NOTA', 'CONFERIDA EM', 'PEDIDO', 'FORNECEDOR', 'ITEM', 'LOTE', 'SITUAÇÃO', 'DIVERGÊNCIA', 'VALIDADE'),
                2: ('REQUISIÇÃO', 'O.S.', 'ITEM', 'LOTE', 'EMBALAGEM', 'A ENTREGAR EM EMBALAGENS', 'SITUAÇÃO', 'DETALHE'),
                3: ('REQUISIÇÃO', 'O.S.', 'ITEM', 'LOTE', 'COM QUEM', 'ENCERRAMENTO DA O.S.', 'DETALHE'),
                4: ('ITEM › LOTE', 'ITEM', 'EM CONFERÊNCIA', 'O.S. COM CUSTÓDIA', 'SITUAÇÃO DO LOTE', 'VALIDADE'),
                5: ('CONTAGEM', 'AJUSTE', 'ITEM', 'LOTE'),
                6: ('REGISTRO', 'MOVIMENTO', 'CONDIÇÃO', 'DOCUMENTO', 'O.S.', 'ITEM', 'LOTE', 'QUANTIDADE', 'SINAL DO APP')}
    IDENT = {1: 'NOTA FISCAL', 2: 'REQUISIÇÃO', 3: 'REQUISIÇÃO', 4: 'ITEM › LOTE', 5: 'CONTAGEM', 6: 'HORA'}
    QRE = r'^[+−-]?[\d.]+(,\d+)? (kg|L|un|sc|t|g|mL)$'   # quantidade com a unidade junto
    def cab_visiveis():   # cabeçalhos à vista com a grade no início (sem rolar a tabela)
        return J(f"(()=>{{const t={TB}; const sc=t.parentElement; sc.scrollLeft=0; const R=sc.getBoundingClientRect(); return [...t.querySelectorAll('[role=columnheader]')].filter(h=>h.getBoundingClientRect().right<=R.right+0.5).map(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());}})()") or []
    def rotulos(col):   # valores oferecidos pelo menu de filtro da coluna (sem a contagem)
        J(f"({TB}).querySelector('button[aria-label=\"Filtrar {col}\"]').click()"); time.sleep(.4)
        r = J("[...document.querySelectorAll('[role=dialog] label')].map(l=>l.innerText.replace(/\\s+\\d+$/,'').trim())") or []
        J("(()=>{const b=[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3); return r
    # seção 1 antes de conferir: a NF 4533 ainda não chegou ("Prevista", data prevista 24/09/2026)
    secao(1); d = dicts(); n33 = next((r for r in d if r.get('NOTA FISCAL') == 'NF 4533'), {})
    chk('seção 1: NF 4533 ainda não chegou: Situação "Prevista", Data da nota 24/09/2026 (prevista), Conferida em —', [n33.get(k) for k in ('SITUAÇÃO', 'DATA DA NOTA', 'CONFERIDA EM')] == ['Prevista', '24/09/2026', '—'], n33)
    # confere a NF 4533 com validade 12/2026 (ano diferente do lote S58-0801, 06/2027): a ordem por data difere da ordem do texto
    J(f"(()=>{{const r=[...({TB}).querySelectorAll('[role=row].g2ed')].find(x=>x.innerText.indexOf('NF 4533')>=0); r.querySelector('[role=cell] span').click();}})()"); time.sleep(.5)
    for k, val in (('conf', '20000'), ('apto', '18000'), ('quar', '2000'), ('obs', '40 sacos com embalagem avariada · aguarda laudo'), ('val', '12/2026')):
        J(f"""(()=>{{const i=document.querySelector('#fx_g_rec_{k}'); const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.15)
    J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.6)
    # trilha com movimentos de vários itens: OS-0430 liberada, 3 itens entregues e confirmados no app, turno de 5 ha fechado (consumo de 3 itens em L)
    J("""(()=>{const X=window.__cen; with(X){ cenMudar(null,c=>cenLiberar(c,'OS-0430')); const c0=cenGet(); const rq=Object.keys(c0.reqs).find(k=>c0.reqs[k].os==='OS-0430');
      cenMudar(null,c=>cenEntregar(c,rq,'Glifosato 480',320,'Marcos','Rui')); cenMudar(null,c=>cenEntregar(c,rq,'2,4-D 806',160,'Marcos','Rui')); cenMudar(null,c=>cenEntregar(c,rq,'Óleo mineral',80,'Marcos','Rui'));
      cenMudar(null,c=>cenConfirmarRecebimento(c,rq)); cenMudar(null,c=>cenIniciarTurno(c,'OS-0430')); return cenMudar(null,c=>cenFecharTurno(c,5,1)).erro||''; } })()""")
    c.goto(f'http://127.0.0.1:{p}/EST.dc.html', 1.4); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    for i in range(1, 7):
        secao(i)
        J("[...document.querySelectorAll('button.g2xtog')].filter(b=>b.offsetParent&&/Expandir tudo/.test(b.innerText)).forEach(b=>b.click())"); time.sleep(.4)   # TAB-12: a pessoa abre tudo (os itens nascem recolhidos)
        for _ in range(2): J(f"[...({TB}).querySelectorAll('button.g2car[aria-expanded=false]')].filter(b=>b.offsetParent).forEach(b=>b.click())"); time.sleep(.3)
        hs = heads(); d = dicts(); shot(f'est{i}-1440')
        chk(f'seção {i}: colunas próprias {", ".join(esperado[i][:4])}…; sem coluna Unidade', all(k in hs for k in esperado[i]) and 'UNIDADE' not in hs and not any(' · ' in h for h in hs), hs)
        # cada quantidade mostrada leva a unidade junto (1ª parte da célula; chips e ações podem vir depois); diferença zero é "0"
        semun = [(h, v) for r in d for h, v in r.items() if h in QTD and v not in ('', '—', '0') and re.match(NUMRE, v.split(' ')[0]) and not re.match(QRE, ' '.join(v.split(' ')[:2]))]
        chk(f'seção {i}: cada quantidade com a unidade junto ("60.000 kg")', not semun, semun[:3])
        chk(f'seção {i}: página sem rolagem horizontal; identificação ({IDENT[i]}) à vista sem rolar a grade', J("document.documentElement.scrollWidth<=innerWidth+1") and IDENT[i] in cab_visiveis(), cab_visiveis()[:4])
        if i == 1:
            nf = next((r for r in d if r.get('NOTA FISCAL') == 'NF 4501'), {}); n33 = next((r for r in d if r.get('NOTA FISCAL') == 'NF 4533'), {})
            chk('seção 1: NF 4501 = 19/09/2026 | PC-088 | Fertisul | KCl 60% | K26-11 | 60.000 kg', [nf.get(k) for k in ('DATA DA NOTA', 'FORNECEDOR', 'ITEM', 'LOTE', 'NA NOTA')] == ['19/09/2026', 'Fertisul', 'KCl 60%', 'K26-11', '60.000 kg'] and nf.get('PEDIDO', '').startswith('PC-088'), nf)
            # "hoje" é a data operacional única da demonstração (dados_config.DIA_OP, 26/09; EST-1 8d0a86c), não mais 23/09
            HOJE = '/'.join(reversed(__import__('dados_config').DIA_OP.split('-')))
            chk(f'seção 1: NF 4533 conferida hoje: Conferida em {HOJE} (data, não "hoje"), validade 12/2026, quarentena 2.000 kg', [n33.get(k) for k in ('CONFERIDA EM', 'VALIDADE', 'QUARENTENA')] == [HOJE, '12/2026', '2.000 kg'], n33)
            filtra('Na nota', ['60.000 kg']); r1 = [r.get('NOTA FISCAL') for r in dicts()]
            chk('seção 1: filtro Na nota = "60.000 kg" (o menu oferece o texto da célula, com a unidade): só a NF 4501', r1 == ['NF 4501'], r1)
            limpa(); ordena('Data da nota'); o1 = [r.get('NOTA FISCAL') for r in dicts()]
            # integração BEN, rodada 1 (BEN-D23): a NF 7731 das caixas do packing (25/09, a conferir) entra na lista do Estoque
            chk('seção 1: ordenar Data da nota (data): NF 4501 (19/09) antes da NF 4533 (24/09) e da NF 7731 das caixas (25/09)', o1 == ['NF 4501', 'NF 4533', 'NF 7731'], o1)
        if i == 2:
            its = sorted({r.get('ITEM') for r in d if r.get('ITEM')}); it0 = its[0] if its else ''
            filtra('Item', [it0]); r2 = [r for r in dicts() if r.get('ITEM')]
            chk(f'seção 2: filtro Item = {it0} corta as outras ({len(its)} itens antes)', len(its) > 1 and r2 and all(r.get('ITEM') == it0 for r in r2), [(r.get('ITEM'), r.get('LOTE')) for r in r2][:4])
            limpa(); ordena('Solicitado', desc=True); v2 = [num(r['SOLICITADO'].split(' ')[0]) for r in dicts() if re.match(NUMRE, r.get('SOLICITADO', '').split(' ')[0])]
            chk('seção 2: ordenar Solicitado decrescente pelo número (a unidade junto não atrapalha)', len(v2) > 1 and v2 == sorted(v2, reverse=True), v2)
            os_ = [r.get('O.S.') for r in dicts()]; chk('seção 2: O.S. em coluna própria (OS-… ou a ordem de beneficiamento OB-…, BEN-D05), separada da requisição (REQ-…)', all(re.match(r'^(OS|OB)-', o or '') for o in os_) and all((r.get('REQUISIÇÃO') or '').startswith('REQ-') for r in dicts()), os_[:3])
        if i == 4:
            kcl = next((r for r in d if r.get('ITEM › LOTE', '').startswith('KCl 60%')), {}); lote = next((r for r in d if r.get('ITEM › LOTE') == 'K26-11'), {})
            chk('seção 4: árvore item › lote; KCl 60% físico 60.000 kg, disponível 50.000 kg; lote K26-11 com Item = KCl 60% e situação "Em quarentena"',
                kcl.get('FÍSICO') == '60.000 kg' and kcl.get('DISPONÍVEL') == '50.000 kg' and lote.get('ITEM') == 'KCl 60%' and lote.get('SITUAÇÃO DO LOTE') == 'Em quarentena', (kcl, lote))
            rr = rotulos('Reservado'); cel = {r.get('RESERVADO') for r in d if r.get('RESERVADO') not in (None, '', '—')}
            chk('seção 4: o menu de filtro de Reservado oferece só valores que aparecem nas células (com unidade) e "(vazio)" para "—"', rr and set(rr) - {'(vazio)'} <= cel and not any(re.match(NUMRE, x) for x in rr), (rr, sorted(cel)))
            ordena('Validade'); sem = [r.get('ITEM › LOTE') for r in dicts() if r.get('ITEM') == 'Semente de soja 58 W' and not r.get('ITEM › LOTE', '').startswith('Semente')]
            chk('seção 4: ordenar Validade (data): S58-0926 (12/2026) antes de S58-0801 (06/2027); pelo texto sairia o contrário', sem == ['S58-0926', 'S58-0801'], sem)
        if i == 6:
            movs6 = sorted({r.get('MOVIMENTO') for r in d}); filtra('Movimento', [movs6[0]] if movs6 else []); r6 = dicts()
            chk('seção 6: filtro Movimento por valor exato', len(movs6) > 1 and r6 and len({r.get('MOVIMENTO') for r in r6}) == 1, (movs6, len(r6)))
            limpa(); res6 = [r for r in dicts() if r.get('MOVIMENTO') == 'Reserva']
            chk('seção 6: reserva com quantidade "320 L" e a condição "reservados" em coluna própria (sem estado colado na quantidade)',
                res6 and all(re.match(QRE, r.get('QUANTIDADE', '')) and r.get('CONDIÇÃO') == 'reservados' for r in res6), [(r.get('QUANTIDADE'), r.get('CONDIÇÃO')) for r in res6][:3])
            ordena('Quantidade', desc=True)
            linhas6 = J(f"[...({TB}).querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>{{const hs=[...r.closest('[role=table]').querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().toUpperCase()); const i=hs.indexOf('QUANTIDADE'); return r.querySelectorAll('[role=cell]')[i].innerText.split('\\n').map(x=>x.trim()).filter(Boolean);}})") or []
            def chave(ls):   # soma quando todas as linhas têm a mesma unidade; senão sem chave (vai para o fim)
                ps = [re.match(QRE, x) and (num(x.split(' ')[0]), x.split(' ')[1]) for x in ls]
                return None if not ps or not all(ps) or len({u for _, u in ps}) > 1 else sum(v for v, _ in ps)
            ks = [chave(ls) for ls in linhas6]; multi = [ls for ls in linhas6 if len(ls) > 1]
            vals = [k for k in ks if k is not None]; fim = ks[len(vals):]
            chk('seção 6: ordenar Quantidade (decrescente) com movimentos de vários itens: pela soma em L, sem misturar dígitos dos itens; sem chave no fim',
                multi and vals == sorted(vals, reverse=True) and all(k is None for k in fim) and ks[:len(vals)] == vals, (multi[:2], ks))
    # 390 px: em cada seção a página não rola e a identificação fica à vista
    c.aparelho(390, 844, 2, True); c.goto(f'http://127.0.0.1:{p}/EST.dc.html', 1.4); r390 = []
    for i in range(1, 7):
        secao(i); r390.append((i, bool(J("document.documentElement.scrollWidth<=innerWidth+1")), IDENT[i] in cab_visiveis()))
    shot('est4-390')
    chk('390 px: as 6 seções sem rolagem da página e com a identificação à vista', all(a and b for _, a, b in r390), r390)
    chk('sem erro de script', not J("window.__e"), J("window.__e"))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
