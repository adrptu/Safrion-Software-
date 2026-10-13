# -*- coding: utf-8 -*-
"""A4 (S2 do Estoque; contrato do PR #47, comentário 6147474674) · teste de tela no Chrome headless (EST.dc.html, Faça contagens), a 1440×1000 e a 390×844.
Glifosato 480, lote G26-14 (1.200 L), contagem INV-2611 e a OS-0430 (reserva 320 L), dados sintéticos. Em cada largura, com o cenário limpo:
  T1 · a reserva depois da contagem não a invalida: a linha segue "Ajuste aguardando aprovação" com "Aprovar ajuste"
  T2 · a entrega depois da contagem a desatualiza: a linha mostra "Desatualizada", o motivo e só "Recontar" (sem "Aprovar ajuste")
  T3 · recusa com motivo: a devolução chega por outra tela sem redesenhar esta; "Aprovar ajuste" mostra a recusa (desatualizada, o movimento,
       "Recontar") e nada muda (ajuste pendente, físico 900 L, sem movimento de ajuste)
  T4 · caminho de recontagem: "Recontar" abre a contagem cega com outro contador; 895 L e a causa; "Aprovar ajuste" aplica 900 → 895 L
  T5 · contagem atual abaixo da reserva (só a 1440): conta 300 L com 320 L reservados, aprova; o lote mostra "Reserva sem físico · 20 L" com dono e
       a entrega de 320 L é recusada
No 90e5f67 (antes da correção) T2–T5 falham: a aprovação aplica a diferença sobre o físico que mudou e a contagem abaixo da reserva é recusada.
Uso: python3 est_a4_nav_test.py   (depois do build e do montar_render; capturas a4_*.png em _probe/)"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

K = 'Glifosato 480|G26-14'
# chip ou botão inteiro dentro da caixa da grade (mesma regra do est_fix2_test.py:10): true, 'teclado' (ação alcançável pelo foco) ou 'rolando'
INTEIRO = """((ts,t)=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>ts.every(x=>r.innerText.indexOf(x)>=0)); if(!r) return 'sem linha';
  const e=[...r.querySelectorAll('button,span')].find(x=>x.innerText.trim()===t); if(!e) return 'sem '+t; const sc=r.closest('[role=table]').parentElement;
  const den=()=>{ const box=sc.getBoundingClientRect(), b=e.getBoundingClientRect(); return b.width>0&&b.left>=box.left-0.5&&b.right<=box.right+0.5; };
  sc.scrollLeft=0; if(den()) return true;
  const f=e.closest('button'); if(f){ f.focus(); f.dispatchEvent(new FocusEvent('focusin',{bubbles:true})); return den()?'teclado':false; }
  e.scrollIntoView({block:'nearest',inline:'nearest'}); return den()?'rolando':false; })"""
OVF = "[document.documentElement.scrollWidth, window.innerWidth]"
ST = f"(()=>{{const l=c.lotes['{K}']; const a=(c.ajustes||[]).filter(x=>x.inv==='INV-2611'); return {{fis:l.fisico,res:l.reservado,aj:a.map(x=>x.id+':'+x.estado),mov:c.movs.filter(m=>m.tipo==='ajuste').length}};}})()"

E = Est()
try:
    def limpo(W, H):
        E.c.size(W, H); E.abrir(); E.J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')"); E.abrir()

    def contar(q, causa):
        E.etapa(5); a = E.clk('Contar INV-2611'); asd = E.aside(); E.setv('fx_g_cnt_cont', str(q)); E.setv('fx_g_cnt_causa', causa); E.salvar(); return a, asd, E.toast()

    def fora():   # página sem rolagem horizontal
        w = E.J(OVF); return w[0] <= w[1] + 1, w

    for W, H in ((1440, 1000), (390, 844)):
        tag = f'{W}'
        print(f'\n== largura {W}×{H}')
        limpo(W, H)
        a, asd, t0 = contar(1100, 'Bombonas avariadas descartadas')
        lib = E.mudar("return cenLiberar(c,'OS-0430');"); RQ = E.cen("Object.keys(c.reqs).find(k=>c.reqs[k].os==='OS-0430')")
        E.abrir(); E.etapa(5); r1 = E.rowtxt('INV-2611')
        E.ok(a == 'ok' and '1.200' not in asd and 'INV-2611' in t0 and 'liberada' in lib and 'Ajuste aguardando aprovação' in r1 and 'Aprovar ajuste' in r1,
             f'T1 {tag}: contagem cega 1.100 L; a reserva de 320 L da OS-0430 depois dela não a invalida (aguardando aprovação, com "Aprovar ajuste")', [a, t0, lib, r1])
        # T2 · entrega pela tela (Entregue por O.S.) depois da contagem
        E.etapa(2); E.row(RQ, 'Glifosato 480'); E.salvar(); te = E.toast(); E.etapa(5); r2 = E.rowtxt('INV-2611'); ok2, w2 = fora()
        E.shot(f'a4_{tag}_t2_desatualizada.png')
        E.ok('entregues' in te and 'Desatualizada' in r2 and 'contagem anterior a 1 movimento do lote · reconte' in r2 and 'Recontar' in r2 and 'Aprovar ajuste' not in r2
             and 'contagem desatualizada a recontar' in E.k() and ok2,
             f'T2 {tag}: entrega de 320 L depois da contagem → linha "Desatualizada", motivo e só "Recontar"; faixa conta 1 a recontar; sem rolagem horizontal', [te[-90:], r2, E.k(), w2])
        # T3 · recusa com motivo: a contagem atual vira desatualizada por outra tela (devolução), sem redesenhar esta
        E.rowbtn('INV-2611', 'Recontar'); asd3 = E.aside(); E.setv('fx_g_cnt_cont', '870'); E.setv('fx_g_cnt_causa', 'Bombona com vazamento'); E.salvar()
        r3a = E.rowtxt('INV-2611'); s3a = E.cen(ST)
        dv = E.mudar(f"return cenDevolver(c,'{RQ}','Glifosato 480',20,true,'Rui');")
        b3 = E.rowbtn('INV-2611', 'Aprovar ajuste'); t3 = E.toast(); s3 = E.cen(ST); r3 = E.rowtxt('INV-2611'); ok3, w3 = fora()
        E.shot(f'a4_{tag}_t3_recusa.png')
        E.ok('Ajuste aguardando aprovação' in r3a and 'devolvidos' in dv and b3 == 'ok'
             and 'A contagem INV-2611' in t3 and 'está desatualizada' in t3 and '1 movimento (devolução de 20 L · ' + RQ + ')' in t3 and 'o físico era 880 L e agora é 900 L' in t3
             and 'Nada foi alterado' in t3 and '(Recontar)' in t3,
             f'T3 {tag}: devolução de 20 L por outra tela; "Aprovar ajuste" é recusado com o motivo e o caminho "Recontar"', [r3a, dv, b3, t3])
        vc = E.J(f"({INTEIRO})({json.dumps(['INV-2611'])},'Desatualizada')"); vb = E.J(f"({INTEIRO})({json.dumps(['INV-2611'])},'Recontar')")
        E.J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('INV-2611')>=0); r&&r.scrollIntoView({block:'center'}); const e=r&&[...r.querySelectorAll('span')].find(x=>x.innerText.trim()==='Desatualizada'); e&&e.scrollIntoView({block:'center',inline:'nearest'});})()"); time.sleep(.3)
        E.shot(f'a4_{tag}_t3_linha.png')
        E.ok(vc in (True, 'teclado', 'rolando') and vb in (True, 'teclado', 'rolando'),
             f'T3c {tag}: o selo "Desatualizada" e o botão "Recontar" aparecem inteiros na caixa da grade (à vista, pelo foco ou rolando a grade)', [vc, vb])
        E.ok(s3['fis'] == 900 and s3['mov'] == 0 and s3['aj'] == s3a['aj'] and s3['aj'][-1].endswith('Aguardando gestor') and s3['res'] == s3a['res']
             and 'Desatualizada' in r3 and 'Aprovar ajuste' not in r3 and ok3,
             f'T3b {tag}: recusa atômica (físico 900 L, ajuste pendente, sem movimento de ajuste) e a linha passa a "Desatualizada" com "Recontar"; sem rolagem horizontal', [s3a, s3, r3, w3])
        # T4 · caminho de recontagem até a aprovação
        E.rowbtn('INV-2611', 'Recontar'); asd4 = E.aside(); cont4 = E.val('fx_g_cnt_contador') if E.J("!!document.querySelector('#fx_g_cnt_contador')") else ''
        E.setv('fx_g_cnt_cont', '895'); E.setv('fx_g_cnt_causa', 'Bombona com vazamento'); E.salvar(); r4a = E.rowtxt('INV-2611')
        E.rowbtn('INV-2611', 'Aprovar ajuste'); t4 = E.toast(); s4 = E.cen(ST); r4 = E.rowtxt('INV-2611')
        E.shot(f'a4_{tag}_t4_recontada.png')
        E.ok('900 L' not in asd4 and 'Ajuste aguardando aprovação' in r4a and 'Ajuste INV-2611' in t4 and 'aprovado por Ana (gestora): −5 L no lote G26-14. Físico 900 L → 895 L.' in t4
             and s4['fis'] == 895 and s4['mov'] == 1 and 'Ajuste aprovado' in r4,
             f'T4 {tag}: "Recontar" abre a contagem cega; 895 L e "Aprovar ajuste" aplicam 900 → 895 L, um movimento', [asd4[:200], cont4, r4a, t4, s4, r4])
    # T5 · contagem atual abaixo da reserva (1440)
    print('\n== T5 · contagem abaixo da reserva (1440×1000)')
    limpo(1440, 1000); lib = E.mudar("return cenLiberar(c,'OS-0430');"); RQ = E.cen("Object.keys(c.reqs).find(k=>c.reqs[k].os==='OS-0430')"); E.abrir()
    a, asd, t5c = contar(300, 'Bombonas avariadas descartadas'); E.rowbtn('INV-2611', 'Aprovar ajuste'); t5 = E.toast(); s5 = E.cen(ST)
    E.etapa(4); E.J("[...document.querySelectorAll('button')].filter(b=>/Expandir tudo/.test(b.innerText)).forEach(b=>b.click())"); time.sleep(.4); l5 = E.rowtxt('G26-14'); E.shot('a4_1440_t5_reserva_sem_fisico.png')
    E.etapa(2); E.row(RQ, 'Glifosato 480'); E.salvar(); e5 = E.err() or E.toast(); s5b = E.cen(ST)
    E.ok('Se aprovado: Reserva sem físico: 20 L' in t5c and 'Físico 1.200 L → 300 L.' in t5 and 'Reserva sem físico: 20 L no lote G26-14 (' + RQ + ')' in t5
         and s5['fis'] == 300 and s5['res'] == 320,
         'T5 contagem 300 L com 320 L reservados: registrada com aviso, aprovada (físico 300 L, reserva 320 L preservada) e o alerta com a requisição e o dono', [t5c[-160:], t5[-260:], s5])
    E.ok('Reserva sem físico · 20 L' in l5 and 'confere: Rui (almoxarife) ou Paula (almoxarife)' in l5 and 'não tem 320 L livres' in e5 and s5b['fis'] == 300,
         'T5b o lote G26-14 mostra "Reserva sem físico · 20 L" com quem confere; a entrega de 320 L é recusada', [l5, e5, s5b])
    E.ok(not E.erros(), 'sem erro de script na tela', E.erros())
finally:
    ok = E.fim()
sys.exit(0 if ok else 1)
