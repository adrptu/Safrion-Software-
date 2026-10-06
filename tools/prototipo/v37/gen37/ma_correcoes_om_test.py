# -*- coding: utf-8 -*-
"""Teste CDP das correções do passo 4 nas ordens e leituras, na tela única MA (PCM simplificado S1–S2):
leitura implausível na conclusão vira aviso a confirmar · quantidade aplicada gera sobra e entra no custo ·
editar só o motivo não troca o autor da resposta (e só o executante edita) · abastecimento com leitura alta ou menor:
Descartar / Confirmar troca de contador · leitura da linha do ativo = última leitura · achado vinculado persiste e aparece na OM ·
falta de peça: Solicitar compra → Registrar recebimento → Liberar · F5 reabre a OM · Tab preso e Esc no painel aberto pelo usuário ·
nenhuma coluna cortada a 1.280 × 800.
Uso: python3 ma_correcoes_om_test.py   (lê _render; zera o cenário em cada bloco)"""
import sys, time
from ma_lib import MA

m = MA(1440, 1100); J = m.J
def abast(aid, cont, op='Beto'):
    m.ir('ativo=' + aid, perfil='Otávio'); m.clk('Registrar abastecimento'); m.clk('Sede · D-118', '#ma-painel')
    m.setv('#ab-vol', '150'); m.setv('#ab-leit', cont); m.clk(op, '#ma-painel'); m.clk('Registrar abastecimento', '#ma-painel'); return m.toast()
try:
    # 1 · leitura absurda na conclusão: aviso a confirmar; corrigir e concluir com aplicado menor que o planejado (sobra no recibo e no custo)
    m.ir('om=OM-0234', perfil='Otávio', limpa=True); m.sem_erro('MA · OM-0234')
    m.clk('Liberar mesmo assim', '#ma-painel')
    m.ir('om=OM-0234', perfil='Zé'); m.clk('Iniciar serviço', '#ma-painel'); m.bloco('Tarefas'); m.responder('Feito')
    m.ok('por Zé (mecânico) às' in m.pan(), 'CTL-3 (R-D4): cada tarefa respondida mostra quem e a hora')
    m.setv('#om-leitura', '29.950'); m.clk('Previsto (5 h)', '#ma-painel'); m.clk('Concluir serviço', '#ma-painel'); p = m.pan(); fase = m.man("m.oms['OM-0234'].etapa")
    m.ok('Concluir com esta leitura' in p and 'acima da última' in p and fase == 'Em execução', 'leitura 29.950 h: aviso a confirmar, a ordem segue Em execução', fase)
    m.clk('Corrigir leitura', '#ma-painel'); time.sleep(.2); foco = J("document.activeElement&&document.activeElement.id")
    m.bloco('Peças'); m.setv('#ma-painel input[aria-label^="Aplicado · Óleo de motor"]', '12'); m.setv('#om-leitura', '2.995'); m.clk('Concluir serviço', '#ma-painel'); c = m.toast()
    m.ok(foco == 'om-leitura' and 'em conferência' in c and 'sobra a devolver: 4 L Óleo de motor 15W-40' in c, 'corrigir a leitura e aplicar 12 de 16 L: sobra de 4 L', [foco, c[:160]])
    m.ir('om=OM-0234', perfil='Otávio'); m.clk('Resolver sobras', '#ma-painel'); m.clk('Encerrar ordem', '#ma-painel'); e = m.toast()
    m.ok('encerrada' in e and 'R$ 2.626,00' in e, 'custo com o aplicado (690 + 12 × 28 + 5 h × 320)', e[:120])
    # 1b · revisão do CTL-3, achado 2: a resposta guarda quem e a hora; editar só o motivo não troca o autor; quem não executa não edita
    m.ir('om=OM-0234', perfil='Otávio', limpa=True); m.clk('Liberar mesmo assim', '#ma-painel')
    m.ir('om=OM-0234', perfil='Zé'); m.clk('Iniciar serviço', '#ma-painel'); m.bloco('Tarefas')
    J("document.querySelector('#ma-painel [aria-label=\"Não feito · Lubrificar pontos de graxa\"]').click()"); time.sleep(.4)
    MOT = '#ma-painel input[aria-label="Motivo · Lubrificar pontos de graxa"]'
    m.setv(MOT, 'sem graxa'); ck0 = m.man("m.oms['OM-0234'].chk[4]") or {}
    m.setv(MOT, 'sem graxa no almoxarifado'); ck = m.man("m.oms['OM-0234'].chk[4]") or {}
    m.ir('om=OM-0234', perfil='Ana'); m.bloco('Tarefas'); ana = J(f"!!document.querySelector('{MOT}')")
    m.ok(ck.get('r') == 'Não feito' and ck.get('por') == 'Zé (mecânico)' and ck.get('em') == ck0.get('em') and ck.get('mot') == 'sem graxa no almoxarifado' and not ana,
         'tarefa: Zé responde "Não feito" e edita o motivo; a resposta segue de Zé com a mesma hora; Ana não edita (Ação de Zé, executante)', [ck, ana])
    # 2 · abastecimento: leitura alta (zero a mais) fica a confirmar e pode ser descartada; leitura menor confirma a troca de contador
    a1 = abast('a02', '29880', 'Beto'); m.ir('vis=ativos&modo=abastecimentos'); r1 = m.linha('AB-1043')
    m.abre('AB-1043'); m.clk('Descartar', '#ma-painel'); d1 = m.toast(); t2 = m.man("m.ativos.a02.leit.val")
    m.ok('acima da última' in a1 and 'A confirmar' in r1 and 'descartada' in d1 and t2 == 2988, 'leitura alta: a confirmar, descartada; Trator 02 segue em 2.988 h', [a1[:100], r1[:120], d1[:100]])
    a2 = abast('cb01', '48100', 'Beto'); m.ir('vis=ativos&modo=abastecimentos'); m.abre('AB-1044'); m.clk('Confirmar troca de contador', '#ma-painel'); c2 = m.toast()
    m.ir('vis=ativos'); lc = m.linha('cb01')
    m.ok('troca de contador' in a2 and 'Troca de contador confirmada' in c2 and '48.100 km' in lc and '49.900 km' in lc and 'Leitura a confirmar' not in lc,
         'troca de contador confirmada: 48.100 km, vencimento ajustado para 49.900 km', [c2[:100], lc[:160]])
    # 3 · Ativos: a leitura da linha = última leitura (abastecimento)
    abast('a04', '3530', 'Beto'); m.ir('vis=ativos'); l4 = m.linha('a04')
    m.ok('3.530 h' in l4 and '3.410 h' not in l4, 'Ativos: leitura do Trator 04 atualizada pelo abastecimento', l4[:120])
    # 4 · achado vinculado à preventiva persiste e aparece na OM
    m.ir('vis=semordem', perfil='Otávio', limpa=True); m.clk('Gerar 3 ordens preventivas'); m.ir('achado=NC-0912'); m.clk('Vincular à OM-0236', '#ma-painel'); v = m.toast()
    m.ir('vis=semordem'); ids = m.linhas(0); m.ir('om=OM-0236'); m.bloco('Origem'); p = m.pan()
    m.ok('vinculad' in v.lower() and 'NC-0912' not in ids and 'NC-0912' in p and m.man("m.achados['NC-0912'].om") == 'OM-0236', 'NC-0912 vinculado: sai de Sem ordem e aparece na OM-0236', [v[:80], ids])
    # 5 · falta de peça: Solicitar compra → Registrar recebimento → Liberar serviço (pontes rotuladas até o 1b/1c)
    m.ir('om=OM-0235'); m.clk('Solicitar compra', '#ma-painel'); s1 = m.toast(); m.clk('Registrar recebimento', '#ma-painel'); s2 = m.toast()
    m.clk('Liberar serviço', '#ma-painel'); s3 = m.toast()
    m.ok('SC-041' in s1 and 'Recebimento da SC-041' in s2 and 'liberad' in s3 and m.man("m.oms['OM-0235'].etapa") == 'Liberadas', 'falta de peça: compra, recebimento e liberação', [s1[:80], s2[:80], s3[:80]])
    # 6 · F5 reabre a OM aberta pela linha
    m.ir('vis=ordens'); m.abre('OM-0228'); h = m.hash(); m.recarregar(); d = m.pan()
    m.ok('om=OM-0228' in h and d.startswith('OM-0228'), f'F5 reabre a OM ({h})', d[:60])
    # 7 · painel aberto pelo usuário: Tab gira dentro; Esc fecha e limpa o endereço do painel
    J("(document.querySelector('#ma-painel button')||document.body).focus()")
    for _ in range(25): m.tecla('Tab', 'Tab', 9)
    dentro = J("!!(document.activeElement&&document.activeElement.closest('#ma-painel'))")
    m.tecla('Escape', 'Escape', 27); time.sleep(.4)
    m.ok(dentro and not J("!!document.querySelector('#ma-painel')&&document.querySelector('#ma-painel').getClientRects().length>0&&document.querySelector('#ma-painel').innerText.indexOf('OM-0228')===0") and 'om=' not in m.hash(),
         f'OM: Tab preso no painel ({dentro}); Esc fecha e limpa o endereço ({m.hash()})')
    # 8 · 1.280 × 800 com ordens geradas: nenhuma grade com rolagem horizontal escondida
    m.c.size(1280, 800); cort = []
    for a in ['plano=PM-07', 'vis=semordem', 'vis=ordens', 'vis=ativos', 'vis=ativos&modo=abastecimentos', 'vis=planos', 'ativo=a02']:
        m.ir(a)
        r = J("[...document.querySelectorAll('[role=table]')].filter(t=>t.getClientRects().length).map(tb=>{const w=tb.closest('.g2rola')||tb.parentElement; return w.scrollWidth-w.clientWidth;})") or []
        if any(x > 1 for x in r): cort.append(a + ' ' + str(r))
    m.ok(not cort, '1.280 px: grades sem coluna cortada', cort)
    m.c.size(1440, 1100); m.sem_erro('fim')
finally:
    rc = m.fim()
sys.exit(rc)
