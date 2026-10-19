# -*- coding: utf-8 -*-
"""Teste CDP da Manutenção na tela única (MA.dc.html, PCM simplificado S1–S3) com as finalidades do matest antigo (MA-01..MA-05 + MA-04det),
agora no endereço novo (ESPECIFICACAO §3.1): sem faixa de telas, grades sem rolagem a 1440 px, sem botão Editar;
Ativos (identidade do CD-03 + comboio, próxima manutenção dos planos, abrir pela linha, condição com motivo, só a OM devolve o T1);
Sem ordem (achados no estado, registrar achado exige ativo, vincular sem OM nova, gerar, mover janela tira o conflito,
propor substituto uma vez, sem link para PL-05); Ordens (sobras e encerramento da OM-0230; painel pela linha com o próximo passo);
OM-0233 (aptidão só com teste válido; encerrar exige destino das retiradas); Abastecimentos (o lançamento abre a origem).
Uso: python3 matest.py   (lê _render; zera o cenário no início)"""
import sys
from ma_lib import MA

m = MA(1440, 1000); J = m.J
SCROLL = "[...document.querySelectorAll('[role=table]')].filter(t=>t.getClientRects().length).map(t=>{const w=t.closest('.g2rola')||t.parentElement; return w.scrollWidth-w.clientWidth;})"
try:
    m.ir('vis=semordem', perfil='Otávio', limpa=True)
    # ---------- comum às 4 visões (antes: comum a MA-01..MA-05) ----------
    for vis in ('semordem', 'ordens', 'ativos', 'planos'):
        m.ir('vis=' + vis); m.sem_erro('MA · ' + vis)
        ov = J(SCROLL) or []
        m.ok(all(x <= 2 for x in ov), f'{vis}: grades sem rolagem horizontal a 1440 px', ov)
        m.ok(J("[...document.querySelectorAll('button')].filter(b=>/^Editar/.test(b.innerText.trim())&&b.getClientRects().length).length") == 0, f'{vis}: sem botões Editar')
        m.ok(not J("!!document.querySelector('nav[aria-label=\"Telas da manutenção\"]')"), f'{vis}: sem a faixa "Telas da manutenção" (D-05; o seletor de visão a substitui)')
    # ---------- Ativos (antes MA-01) ----------
    m.ir('vis=ativos'); ids = m.linhas(0); b = m.body()
    m.ok(len(ids) == 16 and 'Colhedora Axial-Flow 7250' in b and 'S680' not in b and 'Comboio CB-01' in b, f'Ativos: 16 ativos com a identidade do CD-03 + comboio ({len(ids)})')
    m.ok('Vencida' in m.linha('a03') and 'Vence em breve' in m.linha('a02') and 'Sem plano' in m.linha('a07'), 'Ativos: próxima manutenção vem dos planos (Vencida · Vence em breve · Sem plano)', [m.linha('a03'), m.linha('a07')])
    m.abre('a08'); m.ok(m.hash() == '#ativo=a08' and '‹ Ativos' in m.body() and 'Colhedora Axial-Flow 7250' in m.body(), 'Ativos: clique na linha abre o detalhe do ativo (#ativo=a08)', m.hash())
    m.bloco('Situação'); m.clk('Mudar condição'); m.clk('Restringir', '#ma-painel'); m.clk('Restringir Colhedora', '#ma-painel'); t1 = m.toast()
    m.ok('motivo da restrição' in t1 and m.man("m.ativos.a08.cond") == 'Apto', 'condição: restringir exige motivo (nada grava sem ele)', t1)
    m.setv('#cd-motivo-r', 'Ruído no elevador'); m.setv('#ma-painel input[type=date]', '2026-09-30')
    m.J("(()=>{const i=[...document.querySelectorAll('#ma-painel input')].find(i=>!i.id&&i.type!=='date'&&!i.value); if(i){ const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'até 6 km/h'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); } })()")
    m.clk('Restringir Colhedora', '#ma-painel'); t2 = m.toast()
    m.ok(m.man("m.ativos.a08.cond") == 'Restrito' and 'restrito até 30/09' in t2, 'condição: com motivo, limites e prazo a Colhedora fica Restrita (com histórico)', t2)
    m.ir('ativo=a01'); m.bloco('Situação'); m.clk('Mudar condição'); p = m.pan()
    m.ok('Declarar apto' in p and 'OM-0233' in p and 'Apto' not in [x.strip() for x in p.split('\n')[:12] if x.strip() in ('Apto',)], 'Trator T1: só a OM-0233 devolve o ativo (Bloqueado → Apto por "Declarar apto" na ordem)', p[:200])
    # ---------- Sem ordem (antes MA-02 e MA-03) ----------
    m.ir('vis=semordem'); b = m.body(); n0 = len(m.linhas(0))
    m.ok(all(x in b for x in ('INSP-104', 'SM-0150', 'NC-0912', 'PM-02 v2', 'PM-05 v1', 'PM-07 v3')) and n0 == 6, f'Sem ordem: achados do estado e vencimentos sem ordem ({n0} linhas)')
    m.clk('Registrar achado'); m.clk('Registrar achado', '#ma-painel'); t3 = m.toast()
    m.ok('ativo' in t3 and m.pan().startswith('Registrar achado'), 'Registrar achado exige escolher o ativo', t3)
    m.setv('#na-aid', 'a08'); m.clk('Relato', '#ma-painel'); m.clk('Rodado e freios', '#ma-painel'); m.clk('Média', '#ma-painel'); m.clk('Apto', '#ma-painel')
    m.setv('#na-sint', 'Folga na direção'); m.clk('Registrar achado', '#ma-painel'); t4 = m.toast()
    m.ir('vis=semordem')
    m.ok('SM-0153' in t4 and 'registrado' in t4 and len(m.linhas(0)) == n0 + 1, 'novo achado registrado (SM-0153) e na fila Sem ordem', t4)
    no = m.man("Object.keys(m.oms).length"); m.ir('achado=INSP-104'); m.clk('Vincular à OM-0234', '#ma-painel'); t5 = m.toast()
    m.ok('vinculad' in t5.lower() and m.man("Object.keys(m.oms).length") == no and m.man("m.achados['INSP-104'].estado") == 'Na OM', 'vincular o achado à OM-0234 não cria ordem nova', t5)
    m.ir('vis=semordem'); m.clk('Gerar 3 ordens preventivas'); t6 = m.toast()
    m.ok(all(x in t6 for x in ('OM-0235', 'OM-0236', 'OM-0237')) and m.man("Object.keys(m.oms).length") == no + 3, 'gerar: 3 ordens preventivas (OM-0235..0237)', t6)
    m.ir('om=OM-0234'); m.clk('Mover janela para 29/09', '#ma-painel'); t7 = m.toast()
    m.ok(m.man("m.oms['OM-0234'].janIso") == '2026-09-29' and 'Mover janela para' not in m.pan() and 'Conflito · OS-0420' not in m.pan(), 'mover a OM-0234 para 29/09 tira o conflito', t7)
    m.ir('om=OM-0233'); m.bloco('Janela e equipe'); m.clk('Propor substituto', '#ma-painel'); t8 = m.toast(); p = m.pan()
    m.ok('Proposta registrada' in t8 and 'Substituto proposto: Trator 02' in p and 'Propor substituto' not in p, 'propor substituto registra a proposta uma vez (aguarda PCP, simulado)', t8)
    m.ok('PL-05' not in (J("document.body.innerHTML") or ''), 'sem link para impedimentos (PL-05 oculta e fixa · CTL-1)')
    # ---------- Ordens (antes MA-04) ----------
    m.ir('vis=ordens'); m.abre('OM-0230'); m.clk('Resolver sobras', '#ma-painel'); t9 = m.toast()
    m.clk('Encerrar ordem', '#ma-painel'); t10 = m.toast()
    m.ok('devolvidas' in t9 and 'encerrada' in t10 and m.man("m.oms['OM-0230'].etapa") == 'Encerradas', 'OM-0230: resolver sobras (ponte simulada) e encerrar', [t9, t10])
    m.ir('vis=ordens'); m.abre('OM-0228'); p = m.pan()
    m.ok(p.startswith('OM-0228 · Bomba do Pivô 2') and 'Iniciar serviço' in p and 'Planejar e autorizar ordem' not in m.body(), 'clique na linha abre o painel da ordem com o próximo passo', p[:120])
    # ---------- OM-0233 (antes MA-04det) ----------
    m.ir('om=OM-0233', perfil='Zé'); p = m.pan()
    m.ok('Declarar' not in p and 'Falta: teste aprovado' in p, 'OM-0233: sem teste aprovado não há aptidão nem conclusão (o motivo à vista)', p[-200:])
    m.clk('Aprovado', '#ma-painel'); m.clk('Anexar foto e registrar Aprovado', '#ma-painel'); p = m.pan()
    m.ok('2ª tentativa · Aprovado' in p and '1ª tentativa · Reprovado' in p, 'teste: a 2ª tentativa Aprovado entra por acréscimo (as duas à vista)')
    m.setv('#om-leitura', '4320'); m.clk('Previsto (6,5 h)', '#ma-painel'); m.clk('Concluir serviço', '#ma-painel'); t11 = m.toast()
    m.ok(m.man("m.oms['OM-0233'].etapa") == 'Em conferência', 'concluir serviço: Em conferência', t11)
    m.clk('Declarar Trator T1 apto', '#ma-painel'); t12 = m.toast()
    m.ok(m.man("m.ativos.a01.cond") == 'Apto' and 'reprogramação' in t12, 'aptidão declarada (CMD-19) · volta pela reprogramação do PCP', t12)
    m.ir('om=OM-0233', perfil='Otávio'); p = m.pan()
    m.ok('destino e responsável de Bomba hidráulica usada' in p, 'encerrar recusado com peça retirada "A definir" (o motivo à vista)', p[-220:])
    m.ir('om=OM-0233', perfil='Zé'); m.bloco('Peças')
    m.setv('#ma-painel select[aria-label^="Destino · Bomba hidráulica usada"]', 'Garantia'); m.setv('#ma-painel input[aria-label^="Responsável · Bomba hidráulica usada"]', 'Concessionária Case IH')
    m.clk('Registrar destino', '#ma-painel'); t13 = m.toast()
    m.ir('om=OM-0233', perfil='Otávio'); m.clk('Encerrar ordem', '#ma-painel'); t14 = m.toast()
    m.ok('garantia' in t13 and 'encerrada' in t14 and m.man("m.oms['OM-0233'].etapa") == 'Encerradas', 'destino da peça retirada e encerramento da OM-0233', [t13, t14])
    # ---------- Abastecimentos (antes MA-05) ----------
    m.ir('vis=ativos&modo=abastecimentos'); m.abre('AB-1042'); p = m.pan()
    m.ok('AB-1042' in p and '2.988 h' in p and 'Tanque cheio' in p, 'Abastecimentos: o lançamento abre a origem (leitura, método)', p[:160])
    m.sem_erro('fim')
finally:
    rc = m.fim()
sys.exit(rc)
