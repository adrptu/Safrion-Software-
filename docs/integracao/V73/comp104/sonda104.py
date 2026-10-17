"""Sonda Claude do PR #104 (PAINEL-FIXO-2) no navegador, 1440 e 390: cada um dos 4 botões ativado pelo teclado mostra a prévia
"nada foi alterado", não grava no navegador e não deixa confirmação fictícia; CA-02 "Abrir O.S." chega à OS-0417; GE-08 "Registrar liberação
da 2ª parcela" não libera parcela. Uso: GEN37=<gen37> [RENDER_DIR=...]."""
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
SNAP = "JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))"
FALSOS = ['Reaberta · Em execução', 'PP-014', 'Proposta enviada', 'Em revisão agronômica', 'Reabertura pedida', 'Em conferência pelo credor',
          'Certidão enviada', 'Enviar ao credor', 'Enviar para revisão agronômica', 'Solicitar reabertura', 'anexe o documento para destravar']
CASOS = [('CA-02.dc.html', 'Conferir reabertura do saldo', 'OS-0417'), ('GE-02det.dc.html', 'Conferir proposta de parâmetro', 'parâmetro'),
         ('GE-03.dc.html', 'Conferir reabertura de 08/2026', 'Controladoria'), ('GE-08.dc.html', 'Conferir envio ao credor', 'credor')]
def bot(rot): return "[...document.querySelectorAll('button,a')].find(b=>b.textContent.trim().startsWith(%s)&&b.getClientRects().length)" % json.dumps(rot)
def revela(rot):
    # abre só o "⋯ Mais ações" ou o bloco que contém o controle (nada de clicar em tudo)
    return J("""(()=>{const b=[...document.querySelectorAll('button,a')].find(b=>b.textContent.trim().startsWith(%s)); if(!b) return 'nao existe';
      if(b.getClientRects().length) return 'visivel';
      const m=b.closest('[role=menu]'); if(m){ const d=m.closest('details'); if(d){ d.open=true; return 'details'; }
        const op=(m.id&&document.querySelector('[aria-controls="'+m.id+'"]'))||m.parentElement.querySelector('[aria-haspopup]'); if(op){ op.click(); return 'menu'; } }
      const d=b.closest('details'); if(d){ d.open=true; return 'details'; }
      const g=b.closest('[data-g2grp],[aria-expanded]'); return 'oculto:'+(b.closest('[hidden]')?'hidden':'?'); })()""" % json.dumps(rot))
TXT = "document.body.innerText"
for w in (1440, 390):
    c.aparelho(w, 1000 if w > 400 else 844, 1 if w > 400 else 2, w < 400)
    for pg, rot, chave in CASOS:
        c.goto(U('Main.dc.html'), .3); J("localStorage.clear();sessionStorage.clear()")
        c.goto(U(pg), .8); achou = espera(bot(rot))
        como = 'visivel'
        if not achou: como = revela(rot); time.sleep(.4); achou = espera(bot(rot), 3)
        chk(f'{w} {pg}: botão "{rot}" alcançável ({como})', achou, como)
        if not achou: continue
        s0 = J(SNAP); J(bot(rot) + ".focus()"); c.tecla('Enter', 'Enter', 13, '\r'); time.sleep(.7)
        t = J(TXT)
        chk(f'{w} {pg}: Enter mostra a prévia "nada foi alterado" com o assunto ({chave})', 'Prévia · nada foi alterado' in t and chave in t, t[-600:])
        chk(f'{w} {pg}: nada gravado no navegador', J(SNAP) == s0)
        f = [x for x in FALSOS if x in t]
        chk(f'{w} {pg}: nenhuma confirmação fictícia na tela', not f, f)
        chk(f'{w} {pg}: sem painel lateral aberto', not J("!!document.querySelector('[role=dialog]:not([hidden])')&&[...document.querySelectorAll('[role=dialog]')].some(d=>d.getClientRects().length)"))
    # CA-02: Abrir O.S. leva à OS-0417
    c.goto(U('CA-02.dc.html'), .8)
    L = bot('Abrir O.S.')
    como = revela('Abrir O.S.'); time.sleep(.4); tem = espera(L, 4) and 'OS-0417' in J(L + ".getAttribute('href')||''")
    chk(f'{w} CA-02: "Abrir O.S." para a OS-0417 alcançável ({como})', tem, como)
    if tem:
        J(L + ".focus()"); c.tecla('Enter', 'Enter', 13, '\r'); time.sleep(1.2)
        chk(f'{w} CA-02 → OS.dc.html#OS-0417 abre a OS-0417', 'OS.dc.html' in J('location.href') and espera("/OS-0417/.test(document.body.innerText)", 6), J('location.href'))
    # GE-08: 2ª parcela não libera
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear();sessionStorage.clear()")
    c.goto(U('GE-08.dc.html'), .8); B = bot('Registrar liberação da 2ª parcela')
    como = revela('Registrar liberação da 2ª parcela'); time.sleep(.4); tem = espera(B, 3)
    chk(f'{w} GE-08: "Registrar liberação da 2ª parcela" alcançável ({como})', tem, como)
    if tem:
        s0 = J(SNAP); J(B + ".click()"); time.sleep(.6); t = J(TXT)
        chk(f'{w} GE-08: 2ª parcela fica bloqueada (prévia, nenhuma parcela liberada) e nada gravado', 'Nenhuma parcela liberada' in t and J(SNAP) == s0, t[-400:])
    erros = J("(window.__erros||[]).length") if J("typeof window.__erros!=='undefined'") else 0
print(f'RESULTADO: {ok_n} OK · {len(falhas)} falhas'); c.close(); srv.terminate()
sys.exit(1 if falhas else 0)
