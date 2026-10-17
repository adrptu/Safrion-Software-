# -*- coding: utf-8 -*-
"""Planejar safra › etapa 2 › "Talhões e cultivos": agrupado por fazenda e recolhido (proprietário, 17/10/2026: "quando so tem 1 fazenda nao
agrupa por fazenda, só quando tem 2 ou mais. corrija."; "Por padrão coloque sempre os cartoes e tabelas com drill down recolhido, primeiro
usuario tem a visao macro e depois consegue escolher onde precisar detalhar no drill down expandido."; esclarecimento: "esse pedido de dril
down recolhido por fazenda é em planejar safra etapa 2"). TAB-12 e TAB-13 em docs/design-system/padroes-1610.md. Navegador real, dados
sintéticos, a 1440 × 900 e a 390 × 844 (toque).
E1 uma fazenda (Safra 2026/27, Santa Rita): a tabela agrupa por fazenda; uma faixa "Santa Rita", recolhida, com a área (ha) e a contagem
   ("n de N talhões planejados"); nenhum talhão à vista; sem filtro rápido por fazenda (só com duas ou mais).
E2 a seta da faixa (clique) abre a fazenda: os N talhões aparecem um nível abaixo; a seta diz "Recolher Santa Rita…"; clicar de novo recolhe.
E3 duas fazendas (Safrinha 2027 com a Boa Vista incluída pela faixa "Trabalhando em"): duas faixas, as duas recolhidas, cada uma com área e
   contagem; o filtro rápido por fazenda aparece; abrir só a Boa Vista mostra só os talhões dela e a Santa Rita continua recolhida.
E4 teclado: Enter na seta da faixa abre, Espaço recolhe.
E5 Cartões: a faixa vira cartão recolhido (sem a lista de talhões) com a contagem; a seta abre os talhões no cartão.
E6 TAB-13: na tabela aberta, só tem seta a linha com o que abrir (faixa e talhão dividido); o talhão folha não tem seta (nem a de ir).
G  sem erro de JavaScript.
Contraprova: RENDER_DIR=<render da 7d65025> reprova E1 (uma fazenda sem faixa) e E3 (faixas abertas na abertura).
Uso (de gen37/): CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B saf_fazenda_recolhida_test.py · SFR_LARG=1440 ou 390"""
import os, sys, json, time, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
LARGS = [int(x) for x in (os.environ.get('SFR_LARG') or '1440,390').split(',')]
OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + json.dumps(info, ensure_ascii=False)[:1200]), flush=True)
p, srv = servir(R); c = Chrome(); J = c.js; U = lambda x: f'http://127.0.0.1:{p}/{x}'
NAV = [0]
def espera(expr, lim=8.0):
    fim = time.monotonic() + lim
    while time.monotonic() < fim:
        try:
            if J('(()=>{try{return !!(' + expr + ')}catch(e){return false}})()'): return True
        except Exception: pass
        time.sleep(.1)
    return False
def abre(h, w):
    NAV[0] += 1; c.aparelho(w, 900 if w > 500 else 844, 1 if w > 500 else 2, w <= 500)
    c.goto(U('Main.dc.html'), .2); J("localStorage.clear();sessionStorage.clear();localStorage.setItem('safrion.perfilDemo','Ana')")
    c.goto(U(f'SAF.dc.html?r={NAV[0]}#{h}'), 1.2); return espera("document.querySelector('[role=table][data-g2g^=\"g_cult_\"] [role=row][data-rid]')")
# a tabela de talhões à vista: faixas (linhas com data-rid fzg_…), linhas por nível (recuo da 1ª célula) e as setas
TAB = r"""((gid)=>{ const vis=e=>!!e&&e.getClientRects().length>0, N=s=>(s||'').replace(/\s+/g,' ').trim();
 const t=document.querySelector('[role=table][data-g2g="'+gid+'"]'); if(!t||!vis(t)) return null;
 const nv=r=>{ const c0=r.querySelector('.g2c0'); const pl=c0?parseFloat(c0.style.paddingLeft||'8'):8; return Math.round((pl-8)/20); };
 const rs=[...t.querySelectorAll('[role=row][data-rid]')].filter(vis).map(r=>{ const b=r.querySelector('button.g2car[aria-expanded]');
   return {id:r.getAttribute('data-rid'), nv:nv(r), txt:N(r.innerText).slice(0,90), seta:b?b.getAttribute('aria-expanded'):null, lab:b?b.getAttribute('aria-label'):'', ir:!!r.querySelector('.g2drill')}; });
 const qf=[...document.querySelectorAll('[role=group][aria-label=Fazenda]')].some(vis);
 return {rs, faixas:rs.filter(r=>/^fzg_/.test(r.id)), qf}; })"""
def tab(gid): return J(f"{TAB}({json.dumps(gid)})") or {}
def seta_faixa(gid, faz, modo='click'):
    return J("""((gid,faz,modo)=>{ const t=document.querySelector('[role=table][data-g2g="'+gid+'"]'); const r=t&&[...t.querySelectorAll('[role=row][data-rid^="fzg_"]')].find(r=>r.innerText.indexOf(faz)>=0);
      const b=r&&r.querySelector('button.g2car[aria-expanded]'); if(!b) return false; if(modo==='foco'){ b.focus(); return document.activeElement===b; } b.click(); return true; })(%s,%s,%s)""" % (json.dumps(gid), json.dumps(faz), json.dumps(modo)))
def resumo_ok(txt): return bool(re.search(r'\d[\d.,]* ha', txt)) and bool(re.search(r'\d+ de \d+ talh(ão|ões) planejados?', txt))
def total_talhoes(txt):
    m = re.search(r'\d+ de (\d+) talh', txt); return int(m.group(1)) if m else -1
def inclui_boa_vista():
    J("document.getElementById('sfz-add')&&document.getElementById('sfz-add').click()"); espera("!!document.getElementById('sfz-pop')")
    J("(()=>{ const l=[...document.querySelectorAll('#sfz-pop label')].find(l=>l.querySelector('b')&&l.querySelector('b').innerText.trim()==='Boa Vista'); if(l) l.querySelector('input').click(); })()")
    ok = espera("/Boa Vista entrou/.test(document.body.innerText)"); c.tecla('Escape', 'Escape', 27); espera("!document.getElementById('sfz-pop')"); time.sleep(.6); return ok

try:
    for w in LARGS:
        # ---------- E1 · uma fazenda ----------
        abre('saf=S2627&passo=cultivos', w); G1 = 'g_cult_S2627'; t0 = tab(G1)
        fx = t0.get('faixas') or []
        chk(f'E1 {w} uma fazenda: a tabela agrupa por fazenda; faixa "Santa Rita" recolhida com área e contagem; nenhum talhão à vista; sem filtro por fazenda',
            len(fx) == 1 and fx[0]['txt'].startswith('Santa Rita') and fx[0]['seta'] == 'false' and resumo_ok(fx[0]['txt']) and len(t0.get('rs') or []) == 1 and not t0.get('qf'),
            [fx, len(t0.get('rs') or []), t0.get('qf')])
        n_tal = total_talhoes(fx[0]['txt']) if fx else -1
        # ---------- E2 · a seta abre a fazenda ----------
        seta_faixa(G1, 'Santa Rita'); time.sleep(.6); t1 = tab(G1); f1 = (t1.get('faixas') or [{}])[0]
        nv1 = [r for r in (t1.get('rs') or []) if r['nv'] == 1]
        chk(f'E2 {w} a seta da faixa abre a Santa Rita: os {n_tal} talhões aparecem um nível abaixo; a seta diz "Recolher Santa Rita…"',
            f1.get('seta') == 'true' and str(f1.get('lab', '')).startswith('Recolher Santa Rita') and n_tal > 0 and len(nv1) == n_tal, [f1, len(nv1), n_tal, [r['txt'][:20] for r in nv1]])
        # ---------- E6 · TAB-13: seta só na linha com o que abrir ----------
        J("[...document.querySelectorAll('button.g2xtog')].filter(b=>b.getClientRects().length&&/Expandir/.test(b.innerText)).forEach(b=>b.click())"); time.sleep(.6); tx = tab(G1); rs = tx.get('rs') or []
        def tem_filho(i): return i + 1 < len(rs) and rs[i + 1]['nv'] > rs[i]['nv']
        ruins = [r['txt'][:30] for i, r in enumerate(rs) if r['ir'] or (r['seta'] is not None) != tem_filho(i)]
        chk(f'E6 {w} TAB-13 com tudo aberto: seta só na linha que tem linhas filhas (faixa e talhão dividido); talhão folha sem seta e sem seta de ir',
            len(rs) > n_tal and not ruins and any(r['seta'] == 'true' and not r['id'].startswith('fzg_') for r in rs), ruins[:6])
        seta_faixa(G1, 'Santa Rita'); time.sleep(.6); t2 = tab(G1)
        chk(f'E2b {w} clicar de novo na seta recolhe a fazenda (só a faixa à vista)', len(t2.get('rs') or []) == 1 and (t2.get('faixas') or [{}])[0].get('seta') == 'false', t2.get('rs'))
        # ---------- E4 · teclado (tela reaberta: parte do recolhido, sem o "Expandir tudo" do E6) ----------
        abre('saf=S2627&passo=cultivos', w)
        fo = seta_faixa(G1, 'Santa Rita', 'foco'); c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.5); k1 = tab(G1)
        seta_faixa(G1, 'Santa Rita', 'foco'); c.tecla(' ', 'Space', 32, text=' '); time.sleep(.5); k2 = tab(G1)
        chk(f'E4 {w} teclado: Enter na seta da faixa abre a fazenda, Espaço recolhe', fo and len(k1.get('rs') or []) == n_tal + 1 and len(k2.get('rs') or []) == 1, [fo, len(k1.get('rs') or []), len(k2.get('rs') or [])])
        # ---------- E5 · Cartões ----------
        J("(()=>{const b=[...document.querySelectorAll('button[aria-label=\"Cartões\"]')].find(b=>b.getClientRects().length); if(b) b.click();})()"); time.sleep(.8)
        cd = J("""(()=>{ const vis=e=>!!e&&e.getClientRects().length>0; const k=document.querySelector('.g2cartoes[data-g2cd="g_cult_S2627"]'); if(!k||!vis(k)) return null;
          const cs=[...k.querySelectorAll('[role=listitem].g2cd')].filter(vis); const b=cs[0]&&cs[0].querySelector('button.g2car[aria-expanded]');
          return {n:cs.length, t:cs[0]?cs[0].innerText.replace(/\\s+/g,' ').slice(0,90):'', seta:b?b.getAttribute('aria-expanded'):null, kids:[...k.querySelectorAll('.g2cd-kids')].filter(vis).length}; })()""") or {}
        J("(()=>{ const k=document.querySelector('.g2cartoes[data-g2cd=\"g_cult_S2627\"]'); const b=k&&k.querySelector('[role=listitem].g2cd button.g2car[aria-expanded]'); if(b) b.click(); })()"); time.sleep(.6)
        cd2 = J("(()=>{ const vis=e=>!!e&&e.getClientRects().length>0; const k=document.querySelector('.g2cartoes[data-g2cd=\"g_cult_S2627\"]'); return k?[...k.querySelectorAll('.g2cd-kids [role=listitem]')].filter(vis).length:-1; })()")
        chk(f'E5 {w} Cartões: a fazenda é um cartão recolhido (sem a lista de talhões) com área e contagem; a seta abre os {n_tal} talhões no cartão',
            cd.get('n') == 1 and cd.get('seta') == 'false' and cd.get('kids') == 0 and resumo_ok(cd.get('t', '')) and cd2 == n_tal, [cd, cd2])
        J("(()=>{const b=[...document.querySelectorAll('button[aria-label=\"Tabela\"]')].find(b=>b.getClientRects().length); if(b) b.click();})()"); time.sleep(.4)
        # ---------- E3 · duas fazendas ----------
        abre('saf=S27SF&passo=cultivos', w); G2 = 'g_cult_S27SF'; okbv = inclui_boa_vista(); t3 = tab(G2); fx3 = t3.get('faixas') or []
        chk(f'E3 {w} duas fazendas (Boa Vista incluída): duas faixas recolhidas, cada uma com área e contagem; nenhum talhão à vista; filtro por fazenda à vista',
            okbv and len(fx3) == 2 and all(f['seta'] == 'false' and resumo_ok(f['txt']) for f in fx3) and len(t3.get('rs') or []) == 2 and t3.get('qf'), [okbv, fx3, len(t3.get('rs') or []), t3.get('qf')])
        n_bv = next((total_talhoes(f['txt']) for f in fx3 if f['txt'].startswith('Boa Vista')), -1)
        seta_faixa(G2, 'Boa Vista'); time.sleep(.6); t4 = tab(G2)
        sr = next((f for f in (t4.get('faixas') or []) if f['txt'].startswith('Santa Rita')), {}); bv = next((f for f in (t4.get('faixas') or []) if f['txt'].startswith('Boa Vista')), {})
        rs4 = t4.get('rs') or []; i_bv = next((i for i, r in enumerate(rs4) if r['id'] == bv.get('id')), -1)
        abaixo = [r for r in rs4[i_bv + 1:] if r['nv'] >= 1] if i_bv >= 0 else []
        chk(f'E3b {w} abrir só a Boa Vista mostra só os {n_bv} talhões dela; a Santa Rita continua recolhida',
            bv.get('seta') == 'true' and sr.get('seta') == 'false' and n_bv > 0 and len([r for r in rs4 if r['nv'] == 1]) == n_bv and len(abaixo) == n_bv, [sr, bv, [r['txt'][:24] for r in rs4]])
        er = J("(window.__errs||[]).join(' | ')") or ''
        chk(f'G {w} sem erro de JavaScript', not er, er[:300])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas' + (' · ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
