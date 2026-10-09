# -*- coding: utf-8 -*-
"""Teste CDP do processo Estoque (EST.dc.html), em 3 partes independentes (cada uma abre a tela com o cenário limpo, < 40 s):
  python3 esttest.py 1   recebimento com quarentena e validade do lote, NF duplicada, saldos da etapa 4, liberação da quarentena no lote
  python3 esttest.py 2   entregas (O.S. em conferência e impedida só consulta, saldo = solicitado − consumido − custódia), devoluções reabrindo saldo
  python3 esttest.py 3   contagem cega com recontagem por outro contador e causa exigida na aprovação
  python3 esttest.py 4   CTL-3 (aprova quem decide): perfil Rui não aprova nem libera; Rui registra a contagem e Ana aprova sem revisão posterior;
                         trocar o perfil fecha o laudo e o aceite abertos; a entrega grava o perfil de quem entrega
Sem argumento roda as três em sequência (use as partes quando o limite de tempo por comando for curto)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est


def parte1(E):
    print('faixa:', E.J("[...document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ')).join(' | ')"))
    E.ok(E.J("document.querySelector('nav.etp-sec [aria-current=true]').innerText").strip().endswith('Confira recebimentos'), 'abre na seção Confira recebimentos')
    # ---- etapa 4 direta (sem sequência): KCl 60 t físico, 10 t bloqueado, 50 t disponíveis ----
    E.clk('Confira saldos'); t = E.rowtxt('KCl 60%'); print('KCl:', t)
    E.ok('60.000 kg' in t and '10.000 kg' in t and '50.000 kg' in t, 'etapa 4 abre direto; KCl físico 60 t, quarentena 10 t, disponível 50 t')
    E.shot('est_e4a.png')
    # ---- etapa 1: recebimento com quarentena e validade do lote (compras-estoque-07) ----
    E.clk('Confira recebimentos'); print('k1:', E.k()); print('primário:', E.prim())
    print('abrir NF 4533:', E.row('NF 4533'), E.J("document.querySelector('aside[role=dialog] h2').innerText"))
    E.ok(E.J("!!document.querySelector('#fx_g_rec_val') && !document.querySelector('#fx_g_rec_val').readOnly"), 'semente: campo Validade do lote editável')
    E.setv('fx_g_rec_conf', '20000'); E.setv('fx_g_rec_apto', '17000'); E.setv('fx_g_rec_quar', '2000'); E.salvar()
    e = E.err(); print('erro soma:', e); E.ok('somar a conferida' in e, 'apta + quarentena ≠ conferida dá erro no campo')
    E.ok('Informe a validade do lote' in e, 'semente sem validade não salva')
    E.setv('fx_g_rec_apto', '18000'); E.salvar(); e = E.err(); print('erro motivo:', e); E.ok('motivo' in e, 'quarentena exige motivo')
    E.setv('fx_g_rec_obs', '40 sacos com embalagem avariada · aguarda laudo de germinação')
    E.setv('fx_g_rec_val', '13/2027'); E.salvar(); e = E.err(); E.ok('mês/ano' in e, 'validade em formato inválido dá erro', e)
    E.setv('fx_g_rec_val', '08/2026'); E.salvar(); e = E.err(); print('vencido:', e)
    E.ok('Lote vencido em 08/2026' in e and 'Apta para uso = 0' in e, 'lote já vencido exige toda a quantidade em quarentena')
    E.setv('fx_g_rec_val', '03/2027'); E.salvar()
    print('toast:', E.toast()); E.ok(not E.aberto(), 'recebimento salvo com validade')
    t = E.rowtxt('NF 4533'); print('linha:', t); E.ok('Aguarda laudo' in t and '2.000 kg' in t and 'validade 03/2027' in t, 'linha mostra quarentena aguardando laudo e a validade')
    E.ok(E.cen("[c.lotes['Semente de soja 58 W|S58-0926'].fisico, c.lotes['Semente de soja 58 W|S58-0926'].quarentena]") == [20000, 2000], 'recebimento gravado no lote do cenário (20 t, 2 t em quarentena)')
    # integração BEN, rodada 1 (BEN-D23): a NF 7731 das caixas do packing chegou e espera a conferência; com ela pendente o primário do bloco
    # é "Conferir NF 7731" (o "Registrar recebimento" aparece com todas as notas conferidas). Embalagem: unidade un, sem validade, local Packing
    print('abrir NF 7731:', E.row('NF 7731'))
    E.ok(E.J("document.querySelector('#fx_g_rec_val').readOnly && document.querySelector('#fx_g_rec_val').value==='Sem validade' && document.querySelector('#fx_g_rec_local').value==='Packing'"), 'caixa (PC-096): validade travada em Sem validade, local Packing')
    E.setv('fx_g_rec_conf', '1200'); E.setv('fx_g_rec_apto', '1200'); E.setv('fx_g_rec_quar', '0'); E.salvar(); tc = E.toast(); print('toast:', tc)
    E.ok('Recebimento NF 7731 conferido: 1.200 un de Caixa de mamão Formosa 10 kg no lote CX26-02' in tc, 'NF 7731 conferida em un no lote CX26-02', tc)
    # documento duplicado · fertilizante sem validade
    E.clk('Registrar recebimento')
    E.ok(E.J("document.querySelector('#fx_g_rec_val').readOnly && document.querySelector('#fx_g_rec_val').value==='Sem validade'"), 'fertilizante (PC-088): validade travada em Sem validade')
    E.setv('fx_g_rec_nf', 'NF 4533'); E.setv('fx_g_rec_qtd_nf', '1'); E.setv('fx_g_rec_conf', '1'); E.setv('fx_g_rec_apto', '1'); E.setv('fx_g_rec_lote', 'X1'); E.salvar()
    e = E.err(); print('duplicado:', e); E.ok('duplicado' in e and 'validade' not in e, 'NF duplicada não cria segunda entrada (sem exigir validade de fertilizante)')
    E.clk('Cancelar', 'aside[role=dialog]'); E.clk('Descartar alterações', 'aside[role=dialog]')
    E.clk('Confira saldos'); t = E.rowtxt('S58-0926'); print('lote novo:', t)
    E.ok('20.000 kg' in t and '2.000 kg' in t and '18.000 kg' in t, 'saldo: lote S58-0926 20 t físico, 2 t quarentena, 18 t disponível')
    E.ok('03/2027' in t, 'lote novo entra com a validade informada (FEFO usa)')
    t = E.rowtxt('Semente de soja 58 W'); print('item:', t); E.ok('30.000 kg' in t, 'disponível do item 12 t + 18 t = 30 t')
    E.row('S58-0926'); og = E.aside(); E.ok('validade 03/2027' in og, 'origem do lote registra a validade do recebimento', og[:200]); E.fechar()
    # ---- liberar quarentena do KCl no lote, após inspeção (DEMO-02: atualiza e não soma duas vezes) ----
    # CTL-3 (R-D2): liberar exige o nº do laudo e o papel de gestor; sem laudo nada muda e o erro fica junto ao campo
    E.rowbtn('K26-11', 'Liberar após inspeção'); print('sem laudo:', E.clk('Liberar com o laudo'))
    al = E.J("[...document.querySelectorAll('[role=alert]')].map(x=>x.innerText).join(' | ')")
    E.ok('Sem laudo o lote continua bloqueado' in al and E.cen("c.lotes['KCl 60%|K26-11'].quarentena") == 10000, 'CTL-3: sem laudo o KCl segue com 10 t bloqueadas e o erro aparece junto ao campo', al)
    E.setv('est-laudo', 'LAB-0917'); print('com laudo:', E.clk('Liberar com o laudo')); print('toast:', E.toast())
    t = E.rowtxt('KCl 60%'); print('KCl após:', t); E.ok(t.count('60.000 kg') >= 2 and 'Liberar após inspeção' not in E.rowtxt('K26-11'), 'KCl disponível 60 t após a inspeção; botão some do lote')
    E.row('K26-11'); og = E.aside(); E.fechar()
    E.ok('quarentena liberada com o laudo LAB-0917 por Ana (gestora): 10.000 kg passam a disponível' in og, 'CTL-3: a origem do lote registra o laudo e quem liberou', og[:300])
    E.clk('Confira recebimentos'); t = E.rowtxt('NF 4501'); E.ok('Quarentena liberada' in t, 'nota NF 4501 passa a Quarentena liberada', t)


def parte2(E):
    E.clk('Entregue por O.S.'); print('k2:', E.k())
    print('REQ-038:', E.row('REQ-038'), E.aside()[:160])
    E.ok('aguarda a liberação' in E.aside() and E.J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled])').length") == 0, 'REQ-038 bloqueada abre em consulta com motivo')
    E.fechar()
    # compras-estoque-04 · O.S. impedida pela manutenção não recebe material; o já entregue continua registrado
    t = E.rowtxt('REQ-036'); print('REQ-036:', t); E.ok('Bloqueada' in t and 'O.S. impedida · OM-0233' in t and 'Trator T1 bloqueado' in t, 'REQ-036 (OS-0420 impedida) bloqueada com selo e motivo')
    E.row('REQ-036'); a = E.aside(); print('  form:', a[:260])
    E.ok('Nova entrega só com a O.S. apta; o que já foi entregue continua registrado' in a and 'nada foi entregue' not in a, 'REQ-036: subtítulo não diz que nada foi entregue')
    E.ok(E.J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled])').length") == 0, 'REQ-036 só consulta')
    E.fechar()
    # compras-estoque-03 · O.S. em conferência: sem nova entrega, mesmo com saldo pela nova conta (MAP em kg no cenário, saco 50 kg)
    t = E.rowtxt('REQ-031'); print('REQ-031:', t)
    E.ok('O.S. em conferência · sem nova entrega' in t and '1.000 kg' in t and 'saco 50 kg' in t, 'REQ-031 (em conferência) somente consulta com selo; saldo 5.000 − 3.500 − 500 = 1.000 kg')
    E.row('REQ-031'); E.ok(E.J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled])').length") == 0, 'REQ-031 abre só consulta'); E.fechar()
    # REQ-040: o cenário reservou 8.000 kg (tudo o que o lote tinha) dos 11.400 kg da OS-0425
    print('REQ-040:', E.row('REQ-040'), E.val('fx_g_ent_qtd'))
    E.setv('fx_g_ent_qtd', '20000'); E.salvar(); e = E.err(); print('erro:', e)
    E.ok('Acima do saldo a entregar: 8.000 kg (8.000 kg solicitado − 0 kg consumido − 0 kg em custódia)' in e, 'entrega acima do saldo: erro com a conta')
    E.ok(E.val('fx_g_ent_qtd') == '20000', 'valor digitado preservado')
    E.setv('fx_g_ent_qtd', '8000'); E.salvar(); print('toast:', E.toast())
    t = E.rowtxt('REQ-040'); print('linha:', t); E.ok('Entrega completa' in t and 'Aguardando confirmação no app' in t and 'O.S. pede 11.400 kg' in t, 'REQ-040 entregue (8.000 kg), aguardando confirmação no app')
    t = E.rowtxt('REQ-035'); print('REQ-035 antes:', t); E.ok('15 L' in t, 'REQ-035: 175 − 95 − 65 em custódia = 15 L a entregar')
    E.shot('est_e2.png')
    # ---- etapa 3: devolução derruba a custódia ----
    E.clk('Receba devoluções'); print('k3:', E.k())
    t = E.rowtxt('REQ-031'); print('antes:', t); E.ok('Bloqueado' in t and '500 kg em custódia' in t, 'OS-0417 com encerramento bloqueado por 500 kg')
    E.ok('Sem custódia' in E.rowtxt('REQ-036'), 'REQ-036 (bloqueada, já entregue) continua visível em devoluções')
    print('primário:', E.clk('Receber devolução da REQ-031'))
    E.setv('fx_g_dev_qtd', '600'); E.salvar(); e = E.err(); E.ok('Acima da custódia' in e, 'devolução acima da custódia: erro')
    E.setv('fx_g_dev_qtd', '500'); E.salvar(); print('toast:', E.toast())
    t = E.rowtxt('REQ-031'); print('depois:', t); E.ok('Pode encerrar' in t and '1.500 kg' in t, 'custódia 500 → 0, devolvido 1.500 kg, encerramento liberado')
    t = E.rowtxt('REQ-040'); E.ok('8.000 kg' in t, 'REQ-040 aparece com 8.000 kg em custódia')
    # compras-estoque-03 · devolver 30 L da REQ-035 reabre saldo para reentrega (175 − 95 − 35 = 45 L)
    E.row('REQ-035'); E.setv('fx_g_dev_qtd', '30'); E.salvar(); print('toast:', E.toast())
    E.shot('est_e3.png')
    E.clk('Entregue por O.S.'); t = E.rowtxt('REQ-035'); print('REQ-035 depois:', t); E.ok('45 L' in t, 'após devolução de 30 L: 45 L a entregar')
    E.row('REQ-035'); h = E.aside(); E.ok('A entregar: 45 L = 175 L solicitado − 95 L consumido − 35 L em custódia' in h, 'ajuda da quantidade mostra a conta', h[:300])
    E.setv('fx_g_ent_qtd', '46'); E.salvar(); e = E.err(); E.ok('Acima do saldo a entregar: 45 L' in e, '46 L acima do saldo: erro', e)
    E.setv('fx_g_ent_qtd', '45'); E.salvar(); print('toast:', E.toast())
    t = E.rowtxt('REQ-035'); print('REQ-035 reentrega:', t); E.ok('Entrega completa' in t, 'reentrega legítima de 45 L aceita')
    E.clk('Confira saldos'); t = E.rowtxt('M26-07'); print('MAP lote:', t); E.ok('90.500 kg' in t, 'MAP físico 90.000 + 500 kg devolvidos')
    # por coluna (antes, '0 kg' casava dentro de '8.000 kg' e a verificação passava sempre)
    npk = [E.cel('NPK 20-05-20', k) for k in ('Disponível', 'Em custódia (fora do depósito)', 'O.S. com custódia')]; print('NPK:', npk)
    E.ok(npk == ['0 kg', '8.000 kg', 'OS-0425'], 'NPK disponível 0, 8 t em custódia (OS-0425)', npk)
    t = E.rowtxt('F26-02'); print('Fungicida A lote:', t); E.ok('530 L' in t and '65 L' in t, 'Fungicida A: 545 + 30 devolvidos − 45 reentregues = 530 L; reserva da OS-0424 (65 L) preservada')


def parte3(E):
    E.clk('Faça contagens'); print('k5:', E.k())
    t = E.rowtxt('INV-2611'); print('a contar:', t); E.ok('oculto até contar' in t and '1.200' not in t, 'A contar: saldo do sistema oculto')
    print('primário:', E.clk('Contar INV-2611'))
    E.ok('1.200' not in E.aside(), 'formulário da contagem não mostra o saldo')
    E.setv('fx_g_cnt_cont', '1180'); E.salvar(); print('toast:', E.toast())
    E.ok(not E.aberto(), 'salvar sempre grava (sem exigir causa ao contar)')
    t = E.rowtxt('INV-2611'); print('linha:', t); E.ok('aguardando aprovação' in t and 'informe a causa' in t and '1.200 L' in t, 'diferença vira ajuste aguardando aprovação; pede causa')
    E.ok('Recontar' in t and 'Aprovar ajuste' in t, 'linha oferece Recontar e Aprovar ajuste')
    E.clk('Confira saldos'); t = E.rowtxt('G26-14'); print('glifosato:', t); E.ok('1.200 L' in t, 'saldo NÃO muda sem aprovação')
    E.row('G26-14'); og = E.aside(); print('origem:', og[:300]); E.ok('aguardando aprovação' in og, 'origem mostra ajuste pendente não aplicado')
    E.fechar()
    E.clk('Faça contagens'); print('aprovar sem causa:', E.rowbtn('INV-2611', 'Aprovar ajuste'), E.toast())
    E.ok('Informe a causa' in E.toast() and E.aberto(), 'aprovar sem causa pede a causa na contagem')
    E.ok(E.J("document.querySelector('#fx_g_cnt_cont').readOnly && document.querySelector('#fx_g_cnt_contador').disabled"), 'contagem salva: quantidade e contador travados')
    E.setv('fx_g_cnt_causa', '2 bombonas avariadas descartadas sem baixa'); E.salvar(); print('toast:', E.toast()); E.ok('Causa da diferença de INV-2611 registrada' in E.toast(), 'causa registrada sem mudar a contagem')
    print('recontar:', E.rowbtn('INV-2611', 'Recontar'), E.toast())
    E.ok(E.aberto() and E.val('fx_g_cnt_cont') == '', 'Recontar reabre a contagem com quantidade em branco')
    E.ok('Contagem anterior' not in E.aside() and '1.180' not in E.aside(), 'recontagem também é cega (sem contagem anterior no formulário)')
    E.ok('oculto até contar' in E.rowtxt('INV-2611'), 'linha volta a ocultar o saldo')
    E.setv('fx_g_cnt_contador', 'Paula (almoxarife)'); E.setv('fx_g_cnt_cont', '1185'); E.salvar(); e = E.err(); E.ok('outro contador' in e, 'recontagem exige contador diferente', e)
    E.setv('fx_g_cnt_contador', 'Rui (almoxarife)'); E.salvar(); print('toast:', E.toast())
    t = E.rowtxt('INV-2611'); print('recontada:', t); E.ok('−15 L' in t, 'recontagem registrada: diferença −15 L')
    E.row('INV-2611'); og = E.aside(); print('origem:', og[:400]); E.ok('Contagem anterior: 1.180 L por Paula (almoxarife) · diferença −20 L · causa: 2 bombonas' in og, 'contagem anterior fica na origem da linha')
    E.setv('fx_g_cnt_causa', 'Bombona com vazamento separada no descarte'); E.salvar()
    print('aprovar:', E.rowbtn('INV-2611', 'Aprovar ajuste'), E.toast())
    E.ok('Fica revisão posterior pendente (Ana registrou a contagem e decidiu).' in E.toast(), 'CTL-3 (padrão 2): Ana registrou a contagem e aprovou: a decisão vale e fica revisão posterior', E.toast())
    E.clk('Confira saldos'); t = E.rowtxt('G26-14'); print('glifosato:', t); E.ok('1.185 L' in t, 'após aprovação o físico vai a 1.185 L')
    E.shot('est_e4b.png')


def parte4(E):
    # CTL-3 · aprova quem decide (R-D1, R-D2; padrão 2): o perfil de demonstração (menu lateral) é quem age; não é segurança de acesso
    SEL = '[aria-label="Trocar perfil de demonstração"]'
    E.ok(E.J(f"(document.querySelector('{SEL}')||{{value:''}}).value") == 'Ana', 'menu lateral: seletor de perfil começa em Ana')
    print('perfil Rui:', E.setv(SEL, 'Rui'), E.toast()); E.ok('Rui · Almoxarife (não é segurança de acesso)' in E.toast(), 'trocar de perfil avisa que não é segurança de acesso', E.toast())
    E.clk('Faça contagens'); t = E.rowtxt('INV-2609'); print('INV-2609 (Rui):', t)
    E.ok('aprova: Ana (gestora)' in t and 'Aprovar ajuste' not in t and 'Recontar' in t, 'Rui vê "aprova: Ana (gestora)" no lugar de Aprovar ajuste; Recontar continua', t)
    E.clk('Confira saldos'); t = E.rowtxt('K26-11'); print('K26-11 (Rui):', t)
    E.ok('aguarda laudo · Ana (gestora) libera' in t and 'Liberar após inspeção' not in t, 'Rui vê "aguarda laudo · Ana (gestora) libera" no lote em quarentena', t)
    r = E.J("(()=>{const X=window.__cen; const r=X.cenMudar(null,c=>X.cenLiberarQuarentena(c,'KCl 60%|K26-11','LAB-0917',{k:'Rui'})); return r.erro||r.msg;})()")
    E.ok(r == 'Liberar a quarentena do lote K26-11: decisão de Ana (gestora). Nada foi alterado.' and E.cen("c.lotes['KCl 60%|K26-11'].quarentena") == 10000, 'comando direto como Rui é recusado e nada muda', r)
    E.clk('Faça contagens'); print('contar:', E.clk('Contar INV-2611'))
    E.setv('fx_g_cnt_contador', 'Paula (almoxarife)'); E.setv('fx_g_cnt_cont', '1180'); E.setv('fx_g_cnt_causa', 'Bombona avariada descartada sem baixa'); E.salvar(); print('toast:', E.toast())
    reg = E.cen("[(c.ajustes||[]).slice(-1)[0].reg,(c.ajustes||[]).slice(-1)[0].contador]"); t = E.rowtxt('INV-2611')
    E.ok(reg == ['Rui (almoxarife)', 'Paula (almoxarife)'] and 'aprova: Ana (gestora)' in t, 'Rui registra a contagem de Paula: o ajuste guarda quem registrou; a linha diz quem aprova', [reg, t])
    print('perfil Ana:', E.setv(SEL, 'Ana')); t = E.rowtxt('INV-2611'); E.ok('Aprovar ajuste' in t, 'de volta a Ana, a linha oferece Aprovar ajuste', t)
    print('aprovar:', E.rowbtn('INV-2611', 'Aprovar ajuste'), E.toast())
    tt = E.toast(); E.ok('Ajuste INV-2611 (AJ-71) aprovado por Ana (gestora): −20 L no lote G26-14. Físico 1.200 L → 1.180 L.' in tt and 'revisão' not in tt, 'Ana aprova a contagem registrada por Rui: sem revisão posterior', tt)
    E.clk('Confira saldos'); t = E.rowtxt('G26-14'); E.ok('1.180 L' in t, 'G26-14 vai a 1.180 L', t)
    E.shot('est_ctl3_perfil.png')
    # revisão do CTL-3, achado 1: trocar o perfil fecha o que foi aberto para outro perfil (laudo da quarentena; aceite do excedente)
    LAUDO = 'informe o laudo que aprova o material'
    print('liberar K26-11:', E.rowbtn('K26-11', 'Liberar após inspeção')); m0 = E.main()
    print('perfil Rui:', E.setv(SEL, 'Rui')); m1 = E.main(); t = E.rowtxt('K26-11')
    E.ok(LAUDO in m0 and LAUDO not in m1 and 'aguarda laudo · Ana (gestora) libera' in t and E.cen("c.lotes['KCl 60%|K26-11'].quarentena") == 10000,
         'Ana abre o laudo do K26-11 e troca para Rui: o painel do laudo fecha e a linha diz quem libera (quarentena segue 10.000 kg)', [LAUDO in m0, t])
    E.setv(SEL, 'Ana')
    print('relato:', E.mudar("cenIniciarTurno(c,'OS-0421'); return cenFecharTurno(c,10,2,{'Fungicida A':85},'',[]);")); E.abrir(); E.clk('Receba devoluções')
    print('aceitar:', E.rowbtn(['REQ-035', 'Fungicida A'], 'Aceitar consumo')); a0 = E.rowtxt('REQ-035', 'Fungicida A')
    print('perfil Rui:', E.setv(SEL, 'Rui')); a1 = E.rowtxt('REQ-035', 'Fungicida A')
    E.ok('Confirmar aceite' in a0 and 'Confirmar aceite' not in a1 and 'aceite: Ana (gestora)' in a1 and 'Recusar relato' in a1 and E.cen("c.lotes['Fungicida A|F26-02'].fisico") == 545,
         'Ana abre o aceite dos 20 L acima da custódia e troca para Rui: "Confirmar aceite" some, a linha diz "aceite: Ana (gestora)"; F26-02 segue 545 L', [a0, a1])
    # achado 4: a entrega pela tela grava o perfil de quem entrega (antes: sempre "Rui (almoxarife)")
    print('perfil Paula:', E.setv(SEL, 'Paula')); E.mudar("return cenLiberar(c,'OS-0430');"); RQ = E.cen("Object.keys(c.reqs).find(k=>c.reqs[k].os==='OS-0430')")
    E.abrir(); E.clk('Entregue por O.S.'); E.row(RQ, 'Glifosato 480'); E.salvar(); print('toast:', E.toast())
    q = E.cen("c.movs.filter(m=>m.tipo==='entrega').map(m=>m.quem)")
    E.ok(q == ['Paula (almoxarife) → Marcos'], 'Paula entrega o Glifosato da OS-0430 pela tela: a trilha grava "Paula (almoxarife) → Marcos"', q)
    E.setv(SEL, 'Ana')


PARTES = {'1': parte1, '2': parte2, '3': parte3, '4': parte4}
if __name__ == '__main__':
    sel = [a for a in sys.argv[1:] if a in PARTES] or list(PARTES)
    falhas = []
    for k in sel:
        print(f'===== parte {k} =====')
        E = Est()
        try:
            E.abrir(); PARTES[k](E)
            er = E.erros(); E.ok(not er, 'sem erro de script', er)
        except Exception as ex:
            E.ok(False, f'execução da parte {k}', ex)
        finally:
            if not E.fim(): falhas += [f'parte {k}: {f}' for f in E.FAIL]
    print('RESULTADO:', 'OK' if not falhas else ('FALHAS: ' + '; '.join(falhas)))
    sys.exit(0 if not falhas else 1)
