# -*- coding: utf-8 -*-
"""VISOES-2 V2-3 · invariantes gerados do quadro (visoes_marcas.ABRE), dados sintéticos. Para cada listagem do quadro:
E (estático, todas): a grade no HTML gerado tem ess só nas colunas de "Abre com", na ordem, e pq em toda coluna.
No navegador, nas grades visíveis ao abrir a tela (as que dependem de etapa, aba ou painel ficam listadas como "não vistas", sem corte
silencioso):
H 1440: abre exatamente com as colunas de "Abre com", na ordem; "Colunas +N" com N = ocultas (grade com mais de 5 colunas).
A cada opção do "Agrupar por": os grupos aparecem e a soma das linhas dos grupos é o total da Tabela (coluna multivalorada: ≥ total).
D (AGR-02, 16/10) o nome do grupo não desce; a seta do 1º grupo recolhe as linhas dele; "Sem agrupar" volta ao total.
C 390: as 3 primeiras de "Abre com". J sem erro de JS.
Uso: python3 visoes_v23_test.py [página…] (RENDER_DIR=<dir> serve outro _render)."""
import sys, os, time, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import visoes_marcas as VM

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
SO = set(a if a.endswith('.dc.html') else a + '.dc.html' for a in sys.argv[1:])
ok_n = 0; falhas = []; nao_vistas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:500], flush=True)

def grids_da(pg):
    s = open(os.path.join(R, pg), encoding='utf-8').read()
    m = re.search(r'const GRIDS = (\[.*?\]);\nconst NAV', s, re.S)
    return json.loads(m.group(1)) if m else []
alvos = {}
for (pg, gid), abre in VM.QUADRO.items():
    if SO and pg not in SO: continue
    for g in grids_da(pg):
        if g['id'] == gid or (gid.endswith('*') and g['id'].startswith(gid[:-1])):
            alvos.setdefault(pg, []).append((g, abre))
# E · estático
for pg, gs in alvos.items():
    for g, abre in gs:
        ess = sorted([c for c in g['cols'] if c.get('ess')], key=lambda c: c['ess'])
        chk(f'E {pg} {g["id"]}: ess só nas colunas de "Abre com", na ordem, e pq em todas', [c['l'] for c in ess] == abre and all(c.get('pq') for c in g['cols']),
            [[c['l'] for c in ess], abre])
U = lambda p_, x: f'http://127.0.0.1:{p_}/{x}'
HEAD = "((gid)=>[...document.querySelectorAll('[data-g2g=\"'+gid+'\"] [role=columnheader]')].filter(h=>h.getClientRects().length).map(h=>h.innerText.replace(/[⇅▾▴▲▼]/g,'').replace(/\\s+/g,' ').trim()).filter(Boolean))"
VIS = "((gid)=>{const g=document.querySelector('[data-g2g=\"'+gid+'\"]'); return !!g&&g.getClientRects().length>0;})"
LINHAS = "((gid)=>[...document.querySelectorAll('[data-g2g=\"'+gid+'\"] [role=row][data-rid]')].filter(r=>r.getClientRects().length).map(r=>r.getAttribute('data-rid')))"
CONTA = "((gid)=>{const g=document.querySelector('[data-g2g=\"'+gid+'\"]'); const c=g&&g.closest('section,div'); const s=[...document.querySelectorAll('span')].filter(x=>/^\\d+ de \\d+$/.test(x.innerText.trim())&&x.getClientRects().length); return s.map(x=>x.innerText.trim());})"
p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
def norm(x): return x.upper()
def espera(cond, lim=6.0):
    t0 = time.time()
    while time.time() - t0 < lim:
        if J("(()=>{try{return !!(%s)}catch(e){return false}})()" % cond): return True
        time.sleep(.15)
    return False
try:
    for pg, gs in sorted(alvos.items()):
        c.aparelho(1440, 900, 1, False)
        c.goto(U(p, 'Main.dc.html'), .2); J("localStorage.clear();sessionStorage.clear()")
        c.goto(U(p, pg), .5); espera("document.querySelector('[data-g2g]')")
        time.sleep(.4)
        for g, abre in gs:
            gid = g['id']
            if not J(f"({VIS})({json.dumps(gid)})"): nao_vistas.append(f'{pg} {gid}'); continue
            h = J(f"({HEAD})({json.dumps(gid)})") or []
            chk(f'H {pg} {gid}: abre com {abre}', [norm(x) for x in h] == [norm(x) for x in abre], h)
            n_oc = len(g['cols']) - len(abre)
            cvb = J("(()=>{const b=document.querySelector('[data-g2cvb=\"%s\"]'); return b&&b.getClientRects().length?b.innerText.replace(/\\s+/g,' ').trim():'';})()" % gid) or ''
            if len(g['cols']) > 5:
                # o número do botão é o de colunas desmarcadas no painel (a tela pode tirar uma coluna, ex.: Fazenda com uma fazenda escolhida)
                J("document.querySelector('[data-g2cvb=\"%s\"]').click()" % gid) if cvb else None; time.sleep(.35)
                des = J("[...document.querySelectorAll('[data-g2cv=\"%s\"] input[type=checkbox]')].filter(i=>!i.checked).length" % gid) or 0
                J("(()=>{const b=[...document.querySelectorAll('[data-g2cv=\"%s\"] button')].find(b=>/^Fechar$/.test(b.innerText.trim())); if(b) b.click();})()" % gid); time.sleep(.3)
                chk(f'H {pg} {gid}: "Colunas +N" = colunas desmarcadas no painel (≥ {n_oc - 1})', cvb == f'Colunas +{des}' and des >= n_oc - 1, [cvb, des, n_oc])
            base = J(f"({LINHAS})({json.dumps(gid)})") or []
            for d in (g.get('ag') or []):
                r = J("(()=>{const b=document.querySelector('[data-g2agb=\"%s\"]'); if(!b||!b.getClientRects().length) return 'sem botão'; b.click(); return 'ok';})()" % gid); time.sleep(.3)
                r2 = J("(()=>{const m=document.querySelector('[data-g2agm=\"%s\"]'); const i=m&&[...m.querySelectorAll('[role=menuitemradio]')].find(x=>x.innerText.trim().split('\\n')[0].trim()===%s); if(!i) return 'sem item'; i.click(); return 'ok';})()" % (gid, json.dumps(d['l']))); time.sleep(.45)
                gr = J("[...document.querySelectorAll('[data-g2g=\"%s\"] [role=row][data-rid^=\"grp@\"]')].filter(r=>r.getClientRects().length).map(r=>{const m=r.innerText.match(/(\\d+) (item|itens)\\b/); return [r.getAttribute('data-rid'), m?Number(m[1]):-1];})" % gid) or []
                multi = any(cc.get('multi') for cc in g['cols'] if cc['k'] == (d.get('ck') or [''])[0])
                soma = sum(x[1] for x in gr)
                chk(f'A {pg} {gid} Agrupar por {d["l"]}: grupos aparecem e Σ linhas dos grupos {"≥" if multi else "="} total ({len(base)})',
                    r == 'ok' and r2 == 'ok' and len(gr) >= 1 and all(x[1] > 0 for x in gr) and (soma >= len(base) if multi else soma == len(base)), [r, r2, gr[:6], soma, len(base)])
                if gr:
                    k0 = gr[0][0][4:]; n0 = gr[0][1]
                    # AGR-02 (16/10/2026): o nome do grupo não desce; a seta do grupo recolhe as linhas dele, no lugar
                    l0 = [x for x in (J(f"({LINHAS})({json.dumps(gid)})") or []) if not x.startswith('grp@')]
                    dz = J("(()=>{const r=document.querySelector('[data-g2g=\"%s\"] [role=row][data-rid=\"grp@%s\"]'); if(!r) return null; const d=!!r.querySelector('button.g2desce'); const b=r.querySelector('button.g2car'); if(b) b.click(); return {desce:d, seta:!!b};})()" % (gid, k0.replace('"', '\\"'))); time.sleep(.45)
                    ln = [x for x in (J(f"({LINHAS})({json.dumps(gid)})") or []) if not x.startswith('grp@')]
                    J("(()=>{const r=document.querySelector('[data-g2g=\"%s\"] [role=row][data-rid=\"grp@%s\"]'); const b=r&&r.querySelector('button.g2car'); if(b) b.click();})()" % (gid, k0.replace('"', '\\"'))); time.sleep(.3)
                    chk(f'D {pg} {gid} {d["l"]}: o grupo "{k0}" não desce pelo nome; a seta recolhe as {n0} linhas dele', dz and not dz['desce'] and dz['seta'] and len(l0) - len(ln) == n0, [dz, len(l0), len(ln), n0])
                J("(()=>{const b=document.querySelector('[data-g2agb=\"%s\"]'); if(b) b.click();})()" % gid); time.sleep(.3)
                J("(()=>{const m=document.querySelector('[data-g2agm=\"%s\"]'); const i=m&&[...m.querySelectorAll('[role=menuitemradio]')].find(x=>x.innerText.trim().split('\\n')[0].trim()==='Sem agrupar'); if(i) i.click();})()" % gid); time.sleep(.4)
            fim = J(f"({LINHAS})({json.dumps(gid)})") or []
            if g.get('ag'): chk(f'D {pg} {gid}: "Sem agrupar" volta ao total ({len(base)})', len(fim) == len(base), [len(fim), len(base)])
        chk(f'J {pg}: sem erro de JS', not J("(window.__e||[]).length"), J("window.__e"))
        c.aparelho(390, 844, 2, True)
        c.goto(U(p, pg), .5); espera("document.querySelector('[data-g2g]')"); time.sleep(.4)
        for g, abre in gs:
            if not J(f"({VIS})({json.dumps(g['id'])})"): continue
            h = J(f"({HEAD})({json.dumps(g['id'])})") or []
            chk(f'C {pg} {g["id"]} 390: as 3 primeiras de "Abre com"', [norm(x) for x in h] == [norm(x) for x in abre[:3]], h)
finally:
    c.close() if hasattr(c, 'close') else None
print('NÃO VISTAS AO ABRIR (dependem de etapa, aba ou painel; cobertas pelo E): ' + (', '.join(nao_vistas) or 'nenhuma'))
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
