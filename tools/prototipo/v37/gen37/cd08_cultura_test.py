# -*- coding: utf-8 -*-
"""CD08-CULTURA-01 (revisão Codex de 13/10/2026, S2): separar Operações e rendimentos (CD-08) de Culturas e cultivares (CD-02) não pode
romper o vínculo com o cadastro de culturas. Aceite do revisor:
  V1 criar cultura no CD-02 (Sorgo, pela cultivar BRS 373) → no CD-08 a lista Cultura do rendimento oferece Sorgo
  V2 cadastrar rendimento para Sorgo → reabrir o rendimento mostra Sorgo; sair e voltar ao CD-08 mantém o rendimento com custos
  V3 renomear no CD-02 a cultura que tem rendimento específico (Sorgo → Sorgo granífero) → o CD-08 mostra o nome atual, sem o antigo,
     com os mesmos custos (o vínculo é pelo id da cultura)
  V4 a duplicidade por operação + conjunto + cultura continua barrada; "Todas" segue valendo
  V5 voltar ao CD-02 mantém a cultura nova e a cultivar; sem erro de JS
Uso: python3 cd08_cultura_test.py (lê _render)."""
from cadc_lib import T
import time
t = T(); J = t.J
REND = [('conj', 'Trator 05 + Grade niveladora'), ('larg', '4'), ('vel', '7'), ('efic', '75'), ('maq', '120'), ('impl', '30'), ('pess', '1'), ('pess_rs', '38'),
        ('fonte', 'Ensaio da fazenda'), ('vig', '2027-06-30')]
try:
    t.goto('Main.dc.html'); J("localStorage.clear(); sessionStorage.clear(); 1")
    t.goto('CD-02.dc.html')
    t.clk('Criar cultivar'); t.fset('cult', 'Outra cultura…')
    t.fset('nome', 'BRS 373'); t.fset('ncult', 'Sorgo'); t.fset('tipo', 'Anual'); t.fset('unid', 'sc de 60 kg/ha'); t.fset('dias', '120'); t.btn('Salvar'); time.sleep(.3)
    s0 = t.rowtxt(0, 'Sorgo') or ''
    t.goto('CD-08.dc.html'); t.clk('Criar rendimento'); op1 = t.fopts('cult') or []
    t.chk('V1 cultura criada no CD-02 (Sorgo) aparece na lista Cultura do rendimento no CD-08', 'Sorgo 1 cultivar' in s0 and 'Sorgo' in op1 and 'Todas' in op1, [s0, op1])
    t.fset('op', 'Gradagem') if 'Gradagem' in (t.fopts('op') or []) else t.fset('op', (t.fopts('op') or ['', ''])[1])
    opn = t.fv('op')
    for k, val in REND: t.fset(k, val)
    t.fset('cult', 'Sorgo'); t.btn('Salvar'); time.sleep(.3)
    r1 = t.rowtxt(0, 'Trator 05 + Grade niveladora') or ''
    t.openrow(0, 'Trator 05 + Grade niveladora'); c1 = t.fv('cult'); t.btn('Cancelar') if t.isopen() else None; time.sleep(.2)
    if t.isopen(): t.J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>/Fechar|Cancelar/.test(b.innerText)||b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()")
    t.goto('CD-02.dc.html'); t.goto('CD-08.dc.html'); r1b = t.rowtxt(0, 'Trator 05 + Grade niveladora') or ''
    t.chk(f'V2 rendimento de {opn} para Sorgo salvo; reabrir mostra Sorgo; sair e voltar ao CD-08 mantém o rendimento e os custos',
          'Sorgo' in r1 and c1 == 'Sorgo' and r1b == r1, [r1, c1, r1b])
    # V3 · renomear a cultura no CD-02
    t.goto('CD-02.dc.html'); t.openrow(0, 'Sorgo 1 cultivar'); t.fset('nome', 'Sorgo granífero'); t.btn('Salvar'); time.sleep(.3)
    s3 = t.rowtxt(0, 'Sorgo granífero') or ''
    t.goto('CD-08.dc.html'); r3 = t.rowtxt(0, 'Trator 05 + Grade niveladora') or ''
    t.clk('Criar rendimento'); op3 = t.fopts('cult') or []
    t.chk('V3 renomear Sorgo → Sorgo granífero no CD-02: o CD-08 mostra o nome atual no rendimento e na lista, sem o antigo, com os mesmos custos',
          'Sorgo granífero' in s3 and 'Sorgo granífero' in r3 and r3.replace('Sorgo granífero', 'Sorgo') == r1 and 'Sorgo granífero' in op3 and 'Sorgo' not in op3, [s3, r3, op3])
    # V4 · duplicidade
    t.fset('op', opn)
    for k, val in REND: t.fset(k, val)
    t.fset('cult', 'Sorgo granífero'); t.btn('Salvar'); a4 = t.alerts()
    t.fset('cult', 'Todas'); t.btn('Salvar'); time.sleep(.3); a4b = t.alerts(); fechou = not t.isopen()
    t.chk('V4 o mesmo conjunto na mesma operação e cultura é barrado; com "Todas" o rendimento geral é aceito',
          'já tem rendimento' in a4 and fechou and not a4b, [a4, a4b, fechou])
    # V5 · CD-02 mantém a cultura e a cultivar
    t.goto('CD-02.dc.html'); s5 = t.rowtxt(0, 'Sorgo granífero') or ''
    J(f"(()=>{{const r={t.ROW(0, 'Sorgo granífero')}; const b=r&&r.querySelector('[aria-expanded]'); if(b&&b.getAttribute('aria-expanded')!=='true') b.click(); return !!b;}})()"); time.sleep(.3)
    cv5 = t.anyrow(0, 'BRS 373') or ''
    t.chk('V5 voltar ao CD-02 mantém Sorgo granífero com a cultivar BRS 373; sem erro de JS', 'Sorgo granífero 1 cultivar' in s5 and 'BRS 373' in cv5 and not t.errs(), [s5, cv5, t.errs()])
finally:
    n = sum(t.ok); print(f'RESULTADO: {n}/{len(t.ok)} ok'); t.c.close(); t.srv.terminate()
    import sys; sys.exit(0 if t.ok and all(t.ok) else 1)
