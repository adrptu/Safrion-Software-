"""Sonda Claude dos PRs #96 (AGRO-10b) e #97 (AGRO-01/OS-05) no render da composição. Uso: GEN37=<gen37> python3 -B <este>."""
import os, sys, time, json
GEN = os.environ.get('GEN37') or os.getcwd(); sys.path.insert(0, GEN)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(GEN, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK    ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + json.dumps(det, ensure_ascii=False)[:500], flush=True)
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda x: f'http://127.0.0.1:{p}/{x}'
def espera(cond, lim=8.0):
    t0 = time.time()
    while time.time() - t0 < lim:
        if J("(()=>{try{return !!(%s)}catch(e){return false}})()" % cond): return True
        time.sleep(.15)
    return False
def tela(w, pag):
    c.aparelho(w, 1000 if w > 400 else 844, 1 if w > 400 else 2, w < 400)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear();sessionStorage.clear()"); c.goto(U(pag), .8)
SNAP = "JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k).length]))"
DET = r"""(()=>{ const d=[...document.querySelectorAll('details')].find(x=>/Conferir caminho de liberação/.test(x.querySelector('summary')?.textContent||'')&&x.getClientRects().length);
  if(!d) return null; const s=d.querySelector('summary'); const r=s.getBoundingClientRect();
  return {open:d.open, itens:[...d.querySelectorAll('li')].map(l=>l.textContent.trim()), links:[...d.querySelectorAll('a')].map(a=>a.getAttribute('href')), txt:d.innerText,
          alto:Math.round(r.height), lado:document.documentElement.scrollWidth>innerWidth+1}; })()"""
for w in (1440, 390):
    # ---- #96: editar safra sem Estado ----
    tela(w, 'SAF.dc.html#saf=S2627&etapa=1')
    espera("document.querySelector('[data-g2g=g_saf] [data-rid=S2627]')")
    J("""(()=>{ const r=document.querySelector('[data-g2g=g_saf] [data-rid=S2627]'); const b=[...r.querySelectorAll('button,a,[role=button]')].find(x=>/^Editar$/.test(x.textContent.trim())); b&&b.click(); })()""")
    aberto = espera("document.querySelector('[role=dialog] input, aside input, form input')", 6)
    f = J(r"""(()=>{ const box=document.querySelector('[role=dialog]')||document.querySelector('aside'); if(!box) return null;
       const labs=[...box.querySelectorAll('label,legend,[role=group]')].map(x=>(x.getAttribute('aria-label')||x.textContent||'').trim().split('\n')[0]);
       const sels=[...box.querySelectorAll('select')].map(s=>[...s.options].map(o=>o.text));
       return {labs, sels, nome:!!box.querySelector('input:not([type=hidden]):not([disabled])'), lado:document.documentElement.scrollWidth>innerWidth+1}; })()""")
    chk(f'#96 {w}: formulário Editar safra abre', aberto and f is not None, f)
    if f:
        chk(f'#96 {w}: sem campo Estado (nenhum rótulo "Estado", nenhum seletor Rascunho/Em planejamento)',
            not any(l.startswith('Estado') for l in f['labs']) and not any('Em planejamento' in o for s in f['sels'] for o in s), f)
        chk(f'#96 {w}: nome continua editável; sem rolagem lateral', f['nome'] and not f['lado'], f)
    J("document.querySelector('[role=dialog] button[aria-label=Fechar], [role=dialog] .g2x')?.click()"); c.tecla('Escape','Escape',27); time.sleep(.3)
    est = J(r"""(()=>{ const t=document.querySelector('[role=table][data-g2g=g_saf]'); if(!t) return null; const rows=[...t.querySelectorAll('[role=row]')].filter(r=>r.closest('[role=table]')===t);
       const hs=[...rows[0].querySelectorAll('[role=columnheader]')].map(h=>(h.getAttribute('aria-label')||h.innerText||'').replace(/[⇅▾▴▲▼]/g,'').trim());
       const r=rows.find(x=>x.getAttribute('data-rid')==='S2627'); const i=hs.findIndex(h=>/^Estado/.test(h)); if(!r||i<0) return {hs, i};
       const cs=[...r.querySelectorAll('[role=cell]')].filter(x=>x.closest('[role=row]')===r); return {hs, i, val:(cs[i]&&cs[i].innerText||'').trim()}; })()""")
    chk(f'#96 {w}: coluna Estado da safra continua na tabela, com o estado na linha S2627', bool(est) and est.get('i', -1) >= 0 and est.get('val') in ('Em planejamento', 'Rascunho', 'Em planejamento\nSelecionada', 'Rascunho\nSelecionada'), est)
    # ---- #97: PL-04 ----
    tela(w, 'PL-04.dc.html'); espera("document.querySelector('details summary')")
    s0 = J(SNAP); d = J(DET)
    chk(f'#97 PL-04 {w}: controle "Conferir caminho de liberação" presente e fechado', d is not None and not d['open'], d)
    if d:
        J("""(()=>{ const s=[...document.querySelectorAll('details summary')].find(x=>/Conferir caminho/.test(x.textContent)&&x.getClientRects().length); s.focus(); })()""")
        foco = J("document.activeElement&&document.activeElement.tagName")
        c.tecla('Enter', 'Enter', 13, '\r'); time.sleep(.3); d = J(DET)
        chk(f'#97 PL-04 {w}: abre por teclado (foco no resumo + Enter)', foco == 'SUMMARY' and d['open'], {'foco': foco, 'open': d['open']})
        chk(f'#97 PL-04 {w}: lista por O.S. com link de identidade, sem resultado fixo de liberação',
            len(d['itens']) > 0 and all(h and h.startswith('OS.dc.html#OS-') for h in d['links']) and len(d['links']) == len(d['itens'])
            and 'Liberada 1 de 5' not in d['txt'] and 'Nenhuma ordem foi alterada' in d['txt'], d)
        chk(f'#97 PL-04 {w}: abrir não grava nada no cenário (localStorage igual); sem rolagem lateral', J(SNAP) == s0 and not d['lado'], {'antes': s0, 'depois': J(SNAP)})
        c.tecla('Enter', 'Enter', 13, '\r'); time.sleep(.3)
        chk(f'#97 PL-04 {w}: fecha de novo por teclado', not J(DET)['open'])
        alvo = d['links'][0]; J("""(()=>{ const a=[...document.querySelectorAll('details a')].find(x=>x.getClientRects().length||true); a&&a.click(); })()""")
        time.sleep(1.2); oid = alvo.split('#')[1]
        chk(f'#97 PL-04 {w}: "Abrir O.S. ›" abre a própria O.S. ({oid})', espera(f"location.href.includes('OS.dc.html') && document.body.innerText.includes({json.dumps(oid)})", 6), J('location.href'))
    # ---- #97: CA-01 ----
    tela(w, 'CA-01.dc.html'); espera("document.querySelector('[data-g2g=g_os] [role=row]')")
    J("""(()=>{ const t=document.querySelector('[data-g2g=g_os]'); const cb=[...t.querySelectorAll('input[type=checkbox],[role=checkbox]')].find(x=>x.closest('[data-rid]')&&x.getClientRects().length); cb&&cb.click(); })()""")
    time.sleep(.4); s0 = J(SNAP); d = J(DET)
    chk(f'#97 CA-01 {w}: com 1 linha selecionada, aparece o controle de prévia (sem "Liberar selecionadas")',
        d is not None and 'Liberar selecionadas' not in J("document.body.innerText"), d)
    if d:
        J("""(()=>{ const s=[...document.querySelectorAll('details summary')].find(x=>/Conferir caminho/.test(x.textContent)&&x.getClientRects().length); s.focus(); })()""")
        c.tecla('Enter', 'Enter', 13, '\r'); time.sleep(.3); d = J(DET)
        chk(f'#97 CA-01 {w}: abre por teclado; itens com link por identidade; declara que ignora a seleção',
            d['open'] and len(d['itens']) > 0 and all(h.startswith('OS.dc.html#OS-') for h in d['links']) and 'independentemente da seleção' in d['txt'], d)
        chk(f'#97 CA-01 {w}: nada gravado; sem rolagem lateral', J(SNAP) == s0 and not d['lado'])
        c.shot(f'/tmp/claude-0/rev9697_out/ca01_{w}.png')

    # ---- #100: CA-01det "Ajustar produtos e doses do saldo" leva ao ajuste real da OS-0421 ----
    tela(w, 'CA-01det.dc.html'); espera("[...document.querySelectorAll('button')].some(b=>/Ajustar produtos e doses do saldo/.test(b.textContent))")
    txt = J("document.body.innerText")
    chk(f'#100 CA-01det {w}: sem o falso "v3 liberada" na tela', 'v3 liberada' not in txt and 'Ajustar e liberar saldo' not in txt, txt[:300])
    J("""(()=>{ const b=[...document.querySelectorAll('button')].find(x=>/Ajustar produtos e doses do saldo/.test(x.textContent)&&x.getClientRects().length); b.focus(); })()""")
    c.tecla('Enter', 'Enter', 13, '\r')
    foi = espera("location.href.includes('OS.dc.html#OS-0421:ajustar')", 6)
    chk(f'#100 CA-01det {w}: Enter no botão leva a OS.dc.html#OS-0421:ajustar', foi, J('location.href'))
    if foi:
        form = espera("[...document.querySelectorAll('[role=dialog],aside,form')].some(x=>x.getClientRects().length&&/OS-0421/.test(x.innerText)&&x.querySelector('input,select'))", 8)
        f2 = J(r"""(()=>{ const x=[...document.querySelectorAll('[role=dialog],aside,form')].find(x=>x.getClientRects().length&&/OS-0421/.test(x.innerText)); return x?x.innerText.slice(0,400):null; })()""")
        chk(f'#100 CA-01det {w}: o formulário real de ajuste da OS-0421 abre (lê os campos)', form, f2)
print(f'RESULTADO: {ok_n} OK · {len(falhas)} falhas'); c.close(); srv.terminate()
sys.exit(1 if falhas else 0)
