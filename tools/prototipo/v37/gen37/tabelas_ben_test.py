# -*- coding: utf-8 -*-
"""Teste real (Chrome) — tabela das ordens de beneficiamento (BEN.dc.html, g_ob) pelos aceites das tabelas (TF01-TF06; BEN §11.3 T01-T07).
Uma variável por coluna (7 colunas visíveis, plano B do §5.2); quantidade com a unidade na célula e ordem pelo número; filtro rápido por
fase; filtro por valor exato com "(vazio)" na Condição; busca com resultado vazio que diz o que fazer; a 390 px os cartões seguem o
mesmo filtro e a página não rola para o lado. Dados sintéticos. Uso: python3 tabelas_ben_test.py [pasta de capturas]   (< 90 s)"""
import sys, os, time, json, re
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
def linhas(): return J(f"[...({TB}).querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.replace(/\\s+/g,' ').trim()))") or []
def col(nome): hs = heads(); i = hs.index(nome); return [r[i] for r in linhas()]
def filtra(colu, vals):
    J(f"({TB}).querySelector('button[aria-label=\"Filtrar {colu}\"]').click()"); time.sleep(.4)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Limpar').click()"); time.sleep(.2)
    for v in vals: J(f"(()=>{{const l=[...document.querySelectorAll('[role=dialog] label')].find(l=>l.innerText.replace(/\\s+\\d+$/,'').trim()==={json.dumps(v)}); l&&l.querySelector('input').click();}})()"); time.sleep(.15)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='OK').click()"); time.sleep(.5)
def rotulos(colu):
    J(f"({TB}).querySelector('button[aria-label=\"Filtrar {colu}\"]').click()"); time.sleep(.4)
    r = J("[...document.querySelectorAll('[role=dialog] label')].map(l=>l.innerText.replace(/\\s+\\d+$/,'').trim())") or []
    J("(()=>{const b=[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3); return r
def ordena(colu, desc=False):
    J(f"({TB}).querySelector('button[aria-label=\"Filtrar {colu}\"]').click()"); time.sleep(.4)
    J(f"[...document.querySelectorAll('[role=dialog] button.g2fi')][{1 if desc else 0}].click()"); time.sleep(.5)
def limpa(): J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&/^Limpar filtros/.test(b.innerText.trim())); b&&b.click();})()"); time.sleep(.4)
def chip(t): J(f"(()=>{{const b=[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(t)})); b&&b.click();}})()"); time.sleep(.5)
def busca(q):
    J(f"(()=>{{const i=[...document.querySelectorAll('main input')].find(x=>x.offsetParent&&/Buscar/.test(x.placeholder||'')); if(!i) return; const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(q)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"); time.sleep(.6)
def num(t): return float(t.split(' ')[0].replace('.', '').replace(',', '.'))
def shot(n):
    if OUT: c.shot(os.path.join(OUT, n + '.png'))
QRE = r'^[\d.]+(,\d+)? kg$'

try:
    c.aparelho(1440, 900, 1, False)
    c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(f'http://127.0.0.1:{p}/BEN.dc.html', 1.6); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    hs = heads()
    chk('T07 · 7 colunas, uma variável por coluna: Ordem, Produto, Fase, Condição, Em processo, Próximo passo, Quem resolve',
        hs == ['ORDEM', 'PRODUTO', 'FASE', 'CONDIÇÃO', 'EM PROCESSO', 'PRÓXIMO PASSO', 'QUEM RESOLVE'], hs)
    ep = col('EM PROCESSO')
    chk('TF03 · Em processo com a unidade na célula (semente: "0 kg" nas duas), sem coluna de unidade', ep == ['0 kg', '0 kg'] and all(re.match(QRE, x) for x in ep), ep)
    chk('a semente mostra as duas ordens do packing (OB-0110 Em execução, OB-0112 A liberar)', sorted(col('ORDEM')) == ['OB-0110', 'OB-0112'] and set(col('FASE')) == {'Em execução', 'A liberar'}, linhas())
    # filtro rápido por fase (qf): conta e filtra; "Todas" volta
    chip('A liberar'); o1 = col('ORDEM'); chip('Todas'); o2 = col('ORDEM')
    chk('TF02 · filtro rápido "A liberar" deixa só a OB-0112; "Todas" volta às 2', o1 == ['OB-0112'] and len(o2) == 2, [o1, o2])
    # filtro por valor exato na Condição, com "(vazio)" (T01)
    rc = rotulos('Condição')
    chk('T01 · filtro da Condição oferece os selos e "(vazio)"', 'Impedida' in rc and '(vazio)' in rc, rc)
    filtra('Condição', ['(vazio)']); o3 = col('ORDEM'); limpa(); o4 = col('ORDEM')
    chk('T01 · Condição = (vazio) deixa só a ordem sem selo (OB-0110); "Limpar filtros" volta', o3 == ['OB-0110'] and len(o4) == 2, [o3, o4])
    # ordenação numérica pela quantidade (TF04): entrada em processo 0 kg na semente das duas; a ordem pelo ID e pela fase
    ordena('Ordem', desc=True); d1 = col('ORDEM'); ordena('Ordem'); d2 = col('ORDEM')
    chk('TF04 · ordenar por Ordem nos dois sentidos', d1 == ['OB-0112', 'OB-0110'] and d2 == ['OB-0110', 'OB-0112'], [d1, d2])
    # busca: um resultado e nenhum resultado com o que fazer
    busca('OB-0112'); b1 = col('ORDEM'); busca('OB-9999'); b2 = linhas(); vz = J("(document.querySelector('main')||{}).innerText||''") or ''
    busca('')
    chk('TF06 · busca pelo ID acha a OB-0112; busca sem resultado mostra a lista vazia com o caminho de volta', b1 == ['OB-0112'] and b2 == [] and 'Nenhuma linha corresponde aos filtros · Limpar filtros' in vz, [b1, b2, vz[vz.find('Nenhuma'):][:120]])
    # quantidade em processo ordena pelo número e não pelo texto (BEN-REV-06): com 900 kg e 1.800 kg a ordem do texto inverte ("900 kg" > "1.800 kg")
    # fixture só de exibição (a regra do estorno é testada no ben_unit e no ben_fluxo_test): S-02 da OB-0110 estornada deixa 1.800 kg em processo;
    # a OB-0112 em execução com um descarte de 8.370 kg sobre 9.270 kg deixa 900 kg
    J("(()=>{ const c=window.__cen.cenGet(); const o=c.ordens['OB-0110']; const s=o.ben.sai[1]; s.estorno={quem:'teste',em:'2026-09-26 10:00',motivo:'Pesagem refeita'};"
      " const b=c.ordens['OB-0112']; b.etapa='Em execução'; b.ben.nsai=1; b.ben.sai=[Object.assign({},o.ben.sai[2],{id:'S-01',kg:8370,chave:'T-TF04'})];"
      " c.rev=(c.rev||0)+1; localStorage.setItem('talhao-os-cenario-v1',JSON.stringify(c)); })()")
    c.goto(f'http://127.0.0.1:{p}/BEN.dc.html', 1.4); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    ordena('Em processo', desc=True); e1 = col('EM PROCESSO'); ordena('Em processo'); e2 = col('EM PROCESSO')
    chk('TF04 · Em processo ordena pelo número (1.800 kg > 900 kg), não pelo texto (no texto "900 kg" viria antes)', e1 == ['1.800 kg', '900 kg'] and e2 == ['900 kg', '1.800 kg'], [e1, e2])
    lado = J("document.documentElement.scrollWidth>innerWidth+1")
    chk('1440 px sem rolagem lateral da página', lado is False, lado)
    shot('tabelas_ben_1440')
    # 390 px: cartões com o mesmo filtro rápido
    c.aparelho(390, 844, 2, True); J("localStorage.clear(); sessionStorage.clear()")   # a semente de novo: a fixture do TF04 não passa para o celular
    c.goto(f'http://127.0.0.1:{p}/BEN.dc.html', 1.4); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    cards = lambda: J("[...document.querySelectorAll('.pr-card')].filter(x=>x.offsetParent).map(x=>x.innerText.replace(/\\s+/g,' ').trim().split(' · ')[0])") or []
    k0 = cards(); chip('A liberar'); k1 = cards(); chip('Todas')
    lado = J("document.documentElement.scrollWidth>innerWidth+1")
    chk('390 px · cartões com o mesmo filtro rápido ("A liberar" → só a OB-0112) e sem rolagem lateral', len(k0) == 2 and k1 == ['OB-0112'] and lado is False, [k0, k1, lado])
    shot('tabelas_ben_390')
    chk('sem erro de JS', not (J("window.__e") or []), J("window.__e"))
finally:
    try: c.close()
    finally: srv.terminate()
print(f'RESULTADO: {"OK" if not FAIL else "FALHOU"} {len(OK)}/{len(OK) + len(FAIL)}')
sys.exit(1 if FAIL else 0)
