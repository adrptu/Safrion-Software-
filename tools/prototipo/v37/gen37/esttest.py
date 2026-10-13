# -*- coding: utf-8 -*-
"""Teste CDP do Estoque (EST.dc.html) na forma do SUP (4 seções; o painel do registro resolve), em 4 partes independentes (cenário limpo cada):
  python3 esttest.py 1   recebimento: Apta calculada, quarentena com motivo, validade do lote, lote vencido, lote existente com outra validade, NF duplicada,
                         saldo do lote novo; laudo por parcela
  python3 esttest.py 2   requisições: A liberar e O.S. impedida só consulta, entrega até o saldo e a reserva própria, devolução até a custódia reabrindo saldo
  python3 esttest.py 3   contagem cega, causa no mesmo painel, recontagem por outro contador, ajuste aprovado pela gestora
  python3 esttest.py 4   CTL-3 (aprova quem decide): Rui não aprova nem libera; padrão 2 (quem contou e aprova: decisão do gestor registrada · revisão independente pendente, PEND-CTL-02);
                         trocar o perfil fecha o painel aberto; a entrega grava o perfil de quem entrega
A forma mudou (eram 6 etapas, botões na linha); ficam as regras: saldo, reserva própria, custódia, NF duplicada, lote vencido, O.S. impedida,
contagem cega, recontagem e efeito uma vez (docs/suprimentos-simplificado §9.3). Sem argumento roda as quatro."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

SEL = '[aria-label="Trocar perfil de demonstração"]'
EDIT = "document.querySelectorAll('aside[role=dialog] input:not([readonly]):not([disabled]), aside[role=dialog] select:not([disabled]), aside[role=dialog] textarea:not([readonly])').length"


def parte1(E):
    E.perfil('Rui'); E.ir('#sec=recebimentos')
    E.ok(E.secao() == 'Receba e inspecione', 'endereço #sec=recebimentos abre Receba e inspecione', E.secao())
    t = E.rowtxt('NF 4533'); E.ok('Nota prevista' in t, 'NF 4533 ainda não chegou: "Nota prevista"', t)
    # ---- recebimento com quarentena e validade (compras-estoque-07): Apta calculada, motivo obrigatório ----
    E.row('NF 4533'); E.ok(E.J("!!document.querySelector('#fx_g_rec_val') && !document.querySelector('#fx_g_rec_val').readOnly"), 'semente: Validade do lote editável')
    E.setv('fx_g_rec_conf', '20000'); E.setv('fx_g_rec_quar', '2000')
    E.ok(E.val('fx_g_rec_apto') in ('18000', '18.000'), 'Apta calculada: 20.000 − 2.000 = 18.000 (não digitada)', E.val('fx_g_rec_apto'))
    E.clk_prim(); e = E.err(); E.ok('motivo' in e and 'validade' in e.lower(), 'quarentena exige motivo; semente exige validade', e)
    E.setv('fx_g_rec_obs', '40 sacos com embalagem avariada · aguarda laudo de germinação')
    E.setv('fx_g_rec_val', '13/2027'); E.clk_prim(); E.ok('mês/ano' in E.err(), 'validade em formato inválido dá erro', E.err())
    E.setv('fx_g_rec_val', '08/2026'); E.clk_prim(); e = E.err()
    E.ok('Lote vencido em 08/2026' in e and 'apta = 0' in e, 'lote já vencido exige toda a quantidade em quarentena', e)
    # lote existente com outra validade (SUP §9.3; sup_unit N13): o S58-0801 é 06/2027; a nota no mesmo código com 03/2027 é recusada no campo e nada grava
    E.setv('fx_g_rec_lote', 'S58-0801'); E.setv('fx_g_rec_val', '03/2027'); E.clk_prim(); e = E.err()
    E.ok('O lote S58-0801 tem validade 06/2027 e a nota diz 03/2027' in e and E.cen("c.lotes['Semente de soja 58 W|S58-0801'].fisico") == 12000,
         'lote existente (S58-0801, 06/2027) com a validade 03/2027 da nota: recusado no campo, nada gravado', e)
    E.setv('fx_g_rec_lote', 'S58-0926')
    E.setv('fx_g_rec_val', '03/2027'); E.clk_prim()
    st = E.cen("[c.lotes['Semente de soja 58 W|S58-0926'].fisico, c.lotes['Semente de soja 58 W|S58-0926'].quarentena, (cenQuar(c.lotes['Semente de soja 58 W|S58-0926'])[0]||{}).doc]")
    E.ok(st == [20000, 2000, 'NF 4533'], 'recebimento gravado no lote (20 t, 2 t em quarentena como parcela da NF 4533)', st)
    E.ok('Comprovante' in E.aside() and E.prim_painel() == '', 'o painel vira comprovante; a primária some (efeito uma vez)', E.aside()[:120])
    t = E.rowtxt('NF 4533', 'S58-0926'); E.ok('Aguarda laudo' in t and '2.000 kg' in t, 'a parcela da NF 4533 aparece aguardando laudo', t)
    # integração BEN, rodada 1 (BEN-D23): a NF 7731 das caixas do packing chegou e espera a conferência no mesmo painel da nota.
    # Embalagem: unidade un (a do pedido), sem validade, local Packing; o lote novo CX26-02 nasce no Packing com 1.200 un
    t = E.rowtxt('NF 7731'); E.ok('A conferir' in t and '1.200 un' in t, 'NF 7731 (PC-096, caixas) na lista: "A conferir", 1.200 un na nota', t)
    E.row('NF 7731')
    E.ok(E.J("document.querySelector('#fx_g_rec_val').readOnly && document.querySelector('#fx_g_rec_val').value==='Sem validade' && document.querySelector('#fx_g_rec_local').value==='Packing'"),
         'caixa (PC-096): validade travada em "Sem validade", local Packing')
    E.setv('fx_g_rec_conf', '1200'); E.clk_prim(); a7 = E.aside()
    E.ok('Recebimento NF 7731 conferido: 1.200 un de Caixa de mamão Formosa 10 kg no lote CX26-02' in a7, 'NF 7731 conferida em un no lote CX26-02 (comprovante)', a7[:240])
    st7 = E.cen("(function(){ const l=c.lotes['Caixa de mamão Formosa 10 kg|CX26-02']; return l?[l.fisico,l.un,l.local,l.quarentena]:null; })()")
    E.ok(st7 == [1200, 'un', 'Packing', 0], 'lote CX26-02 gravado: 1.200 un no Packing, nada em quarentena', st7)
    # ---- NF duplicada; fertilizante sem validade ----
    E.clk('Registrar NF recebida'); op = E.J("[...document.querySelectorAll('#fx_g_rec_ped option')].map(o=>o.value).find(v=>v.startsWith('PC-088'))") or ''
    E.setv('fx_g_rec_ped', op)
    E.ok(E.J("document.querySelector('#fx_g_rec_val').readOnly && document.querySelector('#fx_g_rec_val').value==='Sem validade'"), 'fertilizante (PC-088): validade travada em "Sem validade"')
    for k, v in (('nf', 'NF 4533'), ('qtd_nf', '1'), ('conf', '1'), ('lote', 'X1')): E.setv('fx_g_rec_' + k, v)
    E.clk_prim(); e = E.err(); E.ok('duplicado' in e and 'validade' not in e.lower(), 'NF duplicada não cria segunda entrada (sem exigir validade do fertilizante)', e)
    E.clk('Cancelar', 'aside[role=dialog]'); E.clk('Descartar alterações', 'aside[role=dialog]')
    # colunas essenciais (proprietário, 10/10): o bloqueado saiu da grade de Lotes e está na conta do painel do lote
    E.ir('#lote=S58-0926'); a = E.aside()
    E.ok(E.cel('S58-0926', 'Físico') == '20.000 kg' and E.cel('S58-0926', 'Disponível') == '18.000 kg' and E.cel('S58-0926', 'Validade') == '03/2027' and '= 20.000 kg − 0 kg − 2.000 kg = 18.000 kg' in a,
         'saldo do lote S58-0926: 20 t físico, 18 t disponíveis, validade 03/2027; no painel, 2 t bloqueadas na conta', [E.cel('S58-0926', k) for k in ('Físico', 'Disponível', 'Validade')] + [a[:160]])
    # ---- laudo por parcela (CTL-3, R-D2; SUP §6): Rui não registra; Ana sem nº não libera; com nº libera só a parcela ----
    E.ir('#nf=NF 4501'); E.ok(E.prim_painel() == '' and 'Laudo: decisão de Ana (gestora)' in E.aside(), 'Rui vê a parcela NF 4501 sem a primária do laudo', E.aside()[:200])
    r = E.mudar("return cenLaudo(c,'KCl 60%|K26-11','NF 4501','LAB-0917','Aprovado','Rui');")
    E.ok(r.startswith('Registrar o laudo da parcela NF 4501 do lote K26-11: decisão de Ana (gestora)') and E.cen("c.lotes['KCl 60%|K26-11'].quarentena") == 10000, 'comando direto como Rui é recusado e nada muda', r)
    E.perfil('Ana'); E.ir('#nf=NF 4501'); E.clk_prim(); e = E.err()
    E.ok('Informe o nº do laudo' in e and E.cen("c.lotes['KCl 60%|K26-11'].quarentena") == 10000, 'sem laudo a parcela segue bloqueada e o erro aparece no campo', e)
    E.setv('fx_g_rec_laudo', 'LAB-0917'); E.setv('fx_g_rec_res', 'Aprovado'); E.clk_prim()
    E.ok(E.cen("[c.lotes['KCl 60%|K26-11'].quarentena, cenDisp(c.lotes['KCl 60%|K26-11'])]") == [0, 60000], 'Ana com LAB-0917: KCl 60 t disponíveis', E.cen("cenDisp(c.lotes['KCl 60%|K26-11'])"))
    E.ir('#lote=K26-11'); og = E.aside()
    E.ok('quarentena liberada com o laudo LAB-0917 por Ana (gestora) (parcela NF 4501): 10.000 kg passam a disponível' in og, 'o painel do lote registra o laudo, a parcela e quem liberou', og[:300])
    E.ok(E.cen("cenQuar(c.lotes['Semente de soja 58 W|S58-0926']).length") == 1, 'a parcela da NF 4533 (outro lote) segue aguardando o seu laudo')


def parte2(E):
    E.perfil('Rui'); E.ir('#req=REQ-038'); a = E.aside()
    E.ok('REQ-038' in a and E.prim_painel() == '' and E.J(EDIT) == 0, 'REQ-038 (O.S. A liberar) abre em consulta', a[:160])
    # compras-estoque-04 · O.S. impedida pela manutenção não recebe material; o já entregue continua registrado
    E.ir('#req=REQ-036'); a = E.aside()
    E.ok('OM-0233' in a and 'entregue 1.560 kg' in a and E.prim_painel() == '' and E.J(EDIT) == 0, 'REQ-036 (OS-0420 impedida): consulta com o motivo; o já entregue continua registrado', a[:300])
    E.ir_secao('Atenda requisições'); E.ok(E.cel('REQ-036', 'Situação') == 'O.S. impedida', 'linha da REQ-036 "O.S. impedida"', E.cel('REQ-036', 'Situação'))
    r = E.mudar("return cenEntregar(c,'REQ-036','Semente de soja 58 W',100,'Carlos','Rui');")
    E.ok('impedida' in r and E.cen("c.reqs['REQ-036'].itens[0].entregue") == 1560, 'a função recusa entregar a O.S. impedida (antes entregava 3.640 kg)', r)
    # compras-estoque-03 · O.S. em conferência: sem nova entrega; o painel é o da sobra
    E.ir('#req=REQ-031'); a = E.aside(); E.ok('Devolução' in a and 'Entregar' not in E.prim_painel(), 'REQ-031 (em conferência): sem nova entrega; o painel recebe a sobra', a[:160])
    # entrega até o saldo e a reserva própria (REQ-040: 8.000 kg reservados dos 11.400 kg da OS-0425)
    E.ir('#req=REQ-040'); E.clk('Entregar parte de NPK 20-05-20 ›', 'aside[role=dialog]'); E.setv('fx_g_req_qtd', '20000'); E.clk_prim(); e = E.err()
    E.ok('Acima do saldo a entregar: 8.000 kg' in e and E.val('fx_g_req_qtd') == '20000', 'entrega acima do saldo: erro com a conta; valor digitado preservado', e)
    E.setv('fx_g_req_qtd', '8000'); E.clk_prim()
    E.ok(E.cen("[c.reqs['REQ-040'].itens[0].entregue,c.reqs['REQ-040'].itens[0].custodia]") == [8000, 8000], 'REQ-040 entregue (8.000 kg em custódia)', E.cen("c.reqs['REQ-040'].itens[0]"))
    E.ir_secao('Atenda requisições'); E.ok(E.cel('REQ-035', 'A entregar') == '15 L', 'REQ-035: 15 L a entregar (reserva própria; antes 0 L reservados)', E.cel('REQ-035', 'A entregar'))
    # devolução derruba a custódia
    E.ir('#req=REQ-031'); E.setv('fx_g_req_dqtd', '600'); E.clk_prim(); E.ok('Acima da custódia' in E.err(), 'devolução acima da custódia: erro', E.err())
    E.setv('fx_g_req_dqtd', '500'); E.clk_prim()
    E.ok(E.cen("[c.reqs['REQ-031'].itens[0].custodia, window.__cen.cenPodeEncerrar(c,'OS-0417')]") == [0, ''], 'custódia 500 → 0; OS-0417 pode encerrar', E.cen("window.__cen.cenPodeEncerrar(c,'OS-0417')"))
    # compras-estoque-03 · devolver 30 L da REQ-035 volta à reserva dela e reabre o saldo (15 + 30 = 45 L)
    E.ir('#req=REQ-035'); E.clk('Registrar devolução de Fungicida A ›', 'aside[role=dialog]'); E.setv('fx_g_req_dqtd', '30'); E.clk_prim()
    E.ir_secao('Atenda requisições'); E.ok(E.cel('REQ-035', 'A entregar') == '45 L', 'após devolução de 30 L: 45 L a entregar', E.cel('REQ-035', 'A entregar'))
    E.ir('#req=REQ-035'); E.clk('Entregar parte de Fungicida A ›', 'aside[role=dialog]'); E.setv('fx_g_req_qtd', '46'); E.clk_prim()
    E.ok('Acima do saldo a entregar: 45 L' in E.err(), '46 L acima do saldo: erro', E.err())
    E.setv('fx_g_req_qtd', '45'); E.clk_prim(); E.ok(E.cen("c.reqs['REQ-035'].itens[0].custodia") == 80, 'reentrega legítima de 45 L aceita (custódia 35 + 45 = 80 L)')
    E.ir_secao('Confira saldos'); t = [E.cel('M26-07', 'Físico'), E.cel('F26-02', 'Físico')]; E.ir('#lote=F26-02'); a = E.aside()   # reservado no painel do lote (10/10)
    E.ok(t == ['90.500 kg', '530 L'] and '= 530 L − 65 L − 0 L' in a and 'Reservado para a REQ-039 (OS-0424): 65 L' in a, 'MAP 90.000 + 500 kg; Fungicida A 545 + 30 − 45 = 530 L; reserva da REQ-039 (65 L) preservada', [t, a[:240]])


def parte3(E):
    E.perfil('Paula'); E.ir('#sec=contagens')
    t = E.rowtxt('INV-2611'); E.ok('A contar' in t and '1.200' not in t, 'A contar: saldo do sistema oculto', t)
    E.row('INV-2611'); E.ok('1.200' not in E.aside() and 'Contagem cega' in E.aside(), 'formulário da contagem não mostra o saldo')
    E.setv('fx_g_cnt_cont', '1180'); E.clk_prim()
    E.ok('Informe a causa' in E.aside() and E.prim_painel() == 'Enviar ajuste à gestora', 'salvar grava a contagem; com diferença o mesmo painel pede a causa', E.aside()[:200])
    E.clk_prim(); E.ok('causa' in E.err().lower(), 'enviar sem causa: erro no campo', E.err())
    E.setv('fx_g_cnt_causa', '2 bombonas avariadas descartadas sem baixa'); E.clk_prim()
    E.ok(E.cen("[(c.ajustes||[]).slice(-1)[0].estado,(c.ajustes||[]).slice(-1)[0].contador,c.lotes['Glifosato 480|G26-14'].fisico]") == ['Aguardando gestor', 'Paula (almoxarife)', 1200], 'ajuste aguardando a gestora com o contador; o saldo não muda')
    # recontagem: quem contou antes não reconta; Rui reconta sem ver a contagem anterior
    E.ir('#sec=contagens'); E.row('INV-2611'); E.clk('Pedir recontagem', 'aside[role=dialog]')
    E.ok(E.val('fx_g_cnt_cont') == '' and '1.180' not in E.aside() and '1.200' not in E.aside(), 'recontagem reabre cega e em branco', E.aside()[:200])
    E.setv('fx_g_cnt_cont', '1185'); E.clk_prim(); E.ok('outro contador' in E.err() or 'outro contador' in E.toast(), 'quem contou antes não reconta', [E.err(), E.toast()])
    E.perfil('Rui'); E.ir('#sec=contagens'); E.row('INV-2611'); E.setv('fx_g_cnt_cont', '1185'); E.clk_prim()
    E.setv('fx_g_cnt_causa', 'Bombona com vazamento separada no descarte'); E.clk_prim()
    E.ok(E.cel('INV-2611', 'Diferença') == '−15 L', 'recontagem registrada: diferença −15 L', E.cel('INV-2611', 'Diferença'))
    E.row('INV-2611'); og = E.aside(); E.ok('Aprova: Ana (gestora)' in og and E.prim_painel() == '', 'Rui vê quem aprova; sem a primária', og[:200])
    E.perfil('Ana'); E.ir('#sec=contagens'); E.row('INV-2611'); p = E.prim_painel(); E.clk_prim()
    E.ok(p == 'Aprovar ajuste · −15 L' and E.cen("c.lotes['Glifosato 480|G26-14'].fisico") == 1185, 'Ana aprova: G26-14 vai a 1.185 L', p)
    E.ok(E.cen("c.movs.filter(m=>m.tipo==='ajuste').length") == 1, 'um movimento de ajuste (efeito uma vez)')


def parte4(E):
    E.ok(E.J(f"(document.querySelector('{SEL}')||{{value:''}}).value") == 'Ana', 'menu lateral: seletor de perfil começa em Ana')
    E.perfil('Rui'); E.ok('não é segurança de acesso' in E.toast(), 'trocar de perfil avisa que não é segurança de acesso', E.toast())
    E.ir('#sec=contagens'); E.row('INV-2609'); a = E.aside()
    E.ok('Aprova: Ana (gestora)' in a and E.prim_painel() == '' and 'Pedir recontagem' in a, 'Rui vê "Aprova: Ana (gestora)" no lugar de Aprovar ajuste; recontagem continua', a[:240])
    # padrão 2 (PEND-CTL-02): Ana conta e aprova → vale e fica "Decisão do gestor registrada · revisão independente pendente"
    E.perfil('Ana'); E.ir('#sec=contagens'); E.row('INV-2611'); E.setv('fx_g_cnt_cont', '1180'); E.clk_prim(); E.setv('fx_g_cnt_causa', 'Bombona avariada descartada sem baixa'); E.clk_prim()
    E.row('INV-2611'); p = E.prim_painel(); E.clk_prim()
    aj = E.cen("(c.ajustes||[]).slice(-1)[0]")
    E.ok(p == 'Aprovar ajuste · −20 L' and aj.get('estado') == 'Aprovado' and aj.get('rev') == 'Decisão do gestor registrada · revisão independente pendente (Ana contou e decidiu)', 'CTL-3 padrão 2 (PEND-CTL-02): Ana contou e aprovou: vale e fica revisão independente pendente', [p, aj.get('rev')])
    # trocar o perfil fecha o painel montado para o perfil anterior (revisão do CTL-3, achado 1)
    E.ir('#nf=NF 4501'); a0 = E.aberto(); E.perfil('Rui')
    E.ok(a0 and not E.aberto() and E.cen("c.lotes['KCl 60%|K26-11'].quarentena") == 10000, 'Ana abre o laudo e troca para Rui: o painel fecha (quarentena segue 10.000 kg)')
    # a entrega pela tela grava o perfil de quem entrega
    E.perfil('Paula'); E.ir('#req=REQ-039'); E.clk_prim()
    q = E.cen("c.movs.filter(m=>m.tipo==='entrega').map(m=>m.quem)")
    E.ok(q == ['Paula (almoxarife) → Marcos'], 'Paula entrega a REQ-039 pela tela: a trilha grava "Paula (almoxarife) → Marcos"', q)
    E.perfil('Ana')


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
