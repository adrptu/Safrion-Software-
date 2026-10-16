# -*- coding: utf-8 -*-
"""CD08-GRAVA-01 (revisão Codex de 14/10/2026, S2): quando o navegador recusa a gravação do cadastro, o salvar não confirma sucesso nem perde
o rascunho; com a gravação de volta, o mesmo Salvar grava uma vez e o dado sobrevive a navegar e recarregar. Falha simulada só na chave dos
cadastros (Storage.prototype.setItem lança QuotaExceededError sintético), como na reprodução do revisor.
  G1 CD-02: cultivar BRS 373 em "Outra cultura" Sorgo com a gravação falhando → formulário segue aberto com o rascunho, alerta e aviso
     "Não salvo", sem Sorgo na lista e nada gravado
  G2 gravação de volta → o mesmo Salvar fecha, mostra "Salvo:" e grava Sorgo e a cultivar uma vez
  G3 recarregar o CD-02 mantém Sorgo; o CD-08 oferece Sorgo na Cultura do rendimento
  G4 CD-08: rendimento de Sorgo com a gravação falhando → não confirma, mantém o rascunho e não cria a linha; de volta → grava; recarregar mantém
  G5 excluir a cultivar (CD-02) com a gravação falhando → "Não excluído", a linha volta e o registro reabre; de volta → exclui e recarregar confirma
  G7 falha só na gravação final (revisão Codex de 14/10, residual S2): cultivar BRS 1501 em "Outra cultura" Milheto → nada gravado (nem
     cultura, nem cultivar, nem a semente nova), formulário aberto com o rascunho; o CD-06 não mostra a semente; repetir sem falha grava
     uma de cada e o CD-06 mostra a semente confirmada
  G6 sem erro de JS
Uso: python3 cad_gravacao_falha_test.py (lê _render)."""
from cadc_lib import T, SETV
import json, time
t = T(); J = t.J
CAD = 'talhao-os-cadastros-v1'
FALHA = ("(()=>{ if(!window.__setItem0) window.__setItem0=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){ if(k==='" + CAD + "') "
         "throw new DOMException('quota sintética','QuotaExceededError'); return window.__setItem0.call(this,k,v); }; return 1; })()")
VOLTA = "(()=>{ if(window.__setItem0) Storage.prototype.setItem=window.__setItem0; return 1; })()"
# G7: só a gravação que já traz a cultivar BRS 1501 falha (as demais gravações da mesma chave passam), como na reprodução do revisor
PARCIAL = ("(()=>{ if(!window.__setItem0) window.__setItem0=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){ if(k==='" + CAD + "'){ let o={}; "
           "try{ o=JSON.parse(v)||{}; }catch(e){} if((o.cultivares||[]).some(p=>(p.kids||[]).some(r=>r.v&&r.v.nome==='BRS 1501'))) "
           "throw new DOMException('quota sintética','QuotaExceededError'); } return window.__setItem0.call(this,k,v); }; return 1; })()")
SEM7 = 'Semente de milheto BRS 1501'
def sementes(): return (J(GRAV) or {}).get('sementes', [])
def cd06_tem(n):   # o CD-06 lê as sementes ao abrir; a busca da tela mostra a linha mesmo com o grupo recolhido
    t.goto('CD-06.dc.html'); J(f"({SETV})('main input[type=search]',{json.dumps(n)})"); time.sleep(.5)
    return bool(J(f"[...document.querySelectorAll('[role=row]')].some(r=>r.innerText.indexOf({json.dumps(n)})>=0)"))
GRAV = f"JSON.parse(localStorage.getItem('{CAD}')||'{{}}')"
REND = [('conj', 'Trator 05 + Grade niveladora'), ('larg', '4'), ('vel', '7'), ('efic', '75'), ('maq', '120'), ('impl', '30'), ('pess', '1'), ('pess_rs', '38'),
        ('fonte', 'Ensaio da fazenda'), ('vig', '2027-06-30')]
def culturas(): return [c['v']['nome'] for c in (J(GRAV) or {}).get('culturas', [])]
def rends(): return [r for o in ((J(GRAV) or {}).get('cd08') or {}).get('rend', []) for r in ([o] + (o.get('kids') or []))]
try:
    t.goto('Main.dc.html'); J("localStorage.clear(); sessionStorage.clear(); 1")
    t.goto('CD-02.dc.html'); J(FALHA)
    t.clk('Cadastrar cultivar'); t.fset('cult', 'Outra cultura…')
    t.fset('nome', 'BRS 373'); t.fset('ncult', 'Sorgo'); t.fset('tipo', 'Anual'); t.fset('unid', 'sc de 60 kg/ha'); t.fset('dias', '120'); t.btn('Salvar'); time.sleep(.3)
    a1, aberto1, n1, c1, s1, g1 = t.alerts(), t.isopen(), t.fv('nome'), t.fv('ncult'), t.rowtxt(0, 'Sorgo'), culturas()
    t.chk('G1 CD-02 com a gravação falhando: formulário aberto com BRS 373/Sorgo, alerta "Não salvo", Sorgo fora da lista e nada gravado',
          aberto1 and 'Não salvo:' in a1 and n1 == 'BRS 373' and c1 == 'Sorgo' and not s1 and 'Sorgo' not in g1, [a1, aberto1, n1, c1, s1, g1])
    J(VOLTA); t.btn('Salvar'); time.sleep(.4)
    s2, g2 = t.rowtxt(0, 'Sorgo') or '', culturas()
    cv2 = [c['v'].get('nome') for p in (J(GRAV) or {}).get('cultivares', []) for c in (p.get('kids') or [])]
    t.chk('G2 gravação de volta: o mesmo Salvar fecha e grava Sorgo e a cultivar BRS 373 uma vez', not t.isopen() and 'Sorgo 1 cultivar' in s2
          and g2.count('Sorgo') == 1 and cv2.count('BRS 373') == 1, [s2, g2, cv2])
    t.goto('CD-02.dc.html'); s3 = t.rowtxt(0, 'Sorgo') or ''
    t.goto('CD-08.dc.html'); t.clk('Cadastrar rendimento'); op3 = t.fopts('cult') or []
    t.chk('G3 recarregar o CD-02 mantém Sorgo; o CD-08 oferece Sorgo na Cultura do rendimento', 'Sorgo 1 cultivar' in s3 and 'Sorgo' in op3, [s3, op3])
    # G4 · CD-08
    J(FALHA)
    t.fset('op', 'Gradagem') if 'Gradagem' in (t.fopts('op') or []) else t.fset('op', (t.fopts('op') or ['', ''])[1])
    for k, val in REND: t.fset(k, val)
    t.fset('cult', 'Sorgo'); n0 = len(rends()); t.btn('Salvar'); time.sleep(.3)
    a4, ab4, cj4, r4 = t.alerts(), t.isopen(), t.fv('conj'), t.rowtxt(0, 'Trator 05 + Grade niveladora')
    J(VOLTA); t.btn('Salvar'); time.sleep(.4); r4b = t.rowtxt(0, 'Trator 05 + Grade niveladora') or ''; n4 = len(rends())
    t.goto('CD-08.dc.html'); r4c = t.rowtxt(0, 'Trator 05 + Grade niveladora') or ''
    t.chk('G4 CD-08 com a gravação falhando: não confirma, mantém o rascunho e não cria a linha; de volta, grava uma vez e recarregar mantém',
          ab4 and 'Não salvo:' in a4 and cj4 == 'Trator 05 + Grade niveladora' and not r4 and 'Sorgo' in r4b and n4 == n0 + 1 and r4c == r4b, [a4, ab4, cj4, r4, r4b, n0, n4, r4c])
    # G5 · excluir a cultivar no CD-02 (o CD-08 não exclui rendimento)
    ABRE = "(()=>{const r=%s; const b=r&&r.querySelector('[aria-expanded]'); if(b&&b.getAttribute('aria-expanded')!=='true') b.click(); return !!b;})()" % t.ROW(0, 'Sorgo')
    cvs = lambda: [c['v'].get('nome') for p in (J(GRAV) or {}).get('cultivares', []) for c in (p.get('kids') or [])]
    t.goto('CD-02.dc.html'); J(ABRE); time.sleep(.3); J(FALHA); d5 = t.delrow(0, 'BRS 373'); time.sleep(.3)
    a5, ab5, r5, to5, g5 = t.alerts(), t.isopen(), t.rowtxt(0, 'BRS 373'), t.toast(), cvs()
    if ab5: t.cancel()
    J(VOLTA); d5b = t.delrow(0, 'BRS 373'); time.sleep(.3); r5b = t.rowtxt(0, 'BRS 373')
    t.goto('CD-02.dc.html'); J(ABRE); time.sleep(.3); r5c = t.rowtxt(0, 'BRS 373'); g5c = cvs()
    t.chk('G5 excluir a cultivar com a gravação falhando: "Não excluído", a linha volta e o registro reabre com o motivo; de volta, exclui e recarregar confirma',
          d5 and ab5 and 'Não excluído:' in a5 and 'Não excluído' in to5 and bool(r5) and 'BRS 373' in g5 and d5b and not r5b and not r5c and 'BRS 373' not in g5c,
          [d5, ab5, a5, to5, r5, g5, d5b, r5b, r5c, g5c])
    # G7 · residual de atomicidade (Codex 6159509677): a semente nova vai na mesma gravação das culturas e cultivares
    def cad7():
        t.clk('Cadastrar cultivar'); t.fset('cult', 'Outra cultura…'); t.fset('nome', 'BRS 1501'); t.fset('ncult', 'Milheto'); t.fset('tipo', 'Anual')
        t.fset('unid', 'sc de 60 kg/ha'); t.fset('dias', '90'); t.btn('Salvar'); time.sleep(.4)
    t.goto('CD-02.dc.html'); J(PARCIAL); cad7()
    a7, ab7, n7, c7, cul7, cv7, sm7 = t.alerts(), t.isopen(), t.fv('nome'), t.fv('ncult'), culturas(), cvs(), sementes()
    J(VOLTA); t.cancel(); v7 = cd06_tem(SEM7)
    t.goto('CD-02.dc.html'); cad7(); ab7b, cul7b, cv7b, sm7b = t.isopen(), culturas(), cvs(), sementes(); v7b = cd06_tem(SEM7)
    t.chk('G7 falha só na gravação final: nada gravado (cultura, cultivar e semente), rascunho aberto e o CD-06 sem a semente; de novo sem falha, '
          'grava uma de cada e o CD-06 mostra a semente',
          ab7 and 'Não salvo:' in a7 and n7 == 'BRS 1501' and c7 == 'Milheto' and 'Milheto' not in cul7 and 'BRS 1501' not in cv7 and SEM7 not in sm7 and not v7
          and not ab7b and cul7b.count('Milheto') == 1 and cv7b.count('BRS 1501') == 1 and sm7b.count(SEM7) == 1 and v7b,
          [sm7, v7, sm7b, v7b, ab7, ab7b, n7, c7, a7[:40], cul7[-2:], cv7[-2:], cul7b[-2:], cv7b[-2:]])
    t.chk('G6 sem erro de JS', not t.errs(), t.errs())
finally:
    n = sum(t.ok); print(f'RESULTADO: {n}/{len(t.ok)} ok'); t.c.close(); t.srv.terminate()
    import sys; sys.exit(0 if t.ok and all(t.ok) else 1)
