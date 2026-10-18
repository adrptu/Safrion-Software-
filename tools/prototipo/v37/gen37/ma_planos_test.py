# -*- coding: utf-8 -*-
"""Teste CDP dos Planos de manutenção girando as preventivas (pedido de 02/10/2026), na tela única MA (PCM simplificado S1–S2):
navegação (ícone Manutenção → MA; visões no seletor da tela) · visão Planos (10 planos, 4 ativos sem plano) · vencimentos calculados (paridade JS × Python) · gerar sem duplicar ·
falta de peça trava a liberação · jornada da OM-0234 (conflito → Liberar mesmo assim → iniciar → tarefas + leitura → concluir fecha o ciclo) ·
publicar v+1 sem mudar a ordem aberta · leitura do abastecimento muda a situação · leitura menor vira troca de contador a confirmar.
Uso: python3 ma_planos_test.py   (lê _render; o cenário é zerado no início)"""
import sys, os
from ma_lib import MA
import dados_manutencao as DM
from ui37 import MENU2

m = MA(1440, 1100); J = m.J
try:
    m.ir('vis=planos', perfil='Otávio', limpa=True); m.sem_erro('MA · Planos')
    # 1 · navegação (13/10/2026, proprietário: barra lateral só com ícones, sem submenus): um ícone Manutenção → tela única MA, destacado e sem
    #     subitens; as 4 visões ficam no seletor da própria tela, Planos por último; #vis=planos abre a visão Planos (antes, v57: 4 subitens no menu)
    g = [x for x in MENU2 if x[0] == 'Manutenção'][0]
    mn = J("[...document.querySelectorAll('nav[aria-label=Menu] a')].filter(a=>/^(MA|MOD-MAN)/.test(a.getAttribute('href')||'')).map(a=>[a.getAttribute('aria-label'),a.getAttribute('href'),a.getAttribute('aria-current'),a.innerText.trim()])")
    vs = J("[...document.querySelectorAll('main .ma-vis button')].map(b=>[b.innerText.replace(/\\s*\\d+\\s*$/,'').trim(),b.getAttribute('aria-pressed')])")
    m.ok(g[2][0] == ('Painel', 'PG.dc.html#mod=man') and all(h.split('#')[0] == 'MA.dc.html' for _, h in g[2][1:]) and mn == [['Manutenção', 'MOD-MAN.dc.html', 'page', '']]   # v60: o ícone abre a tela de entrada; v65: o Painel (PMAN) é o 1º atalho
         and vs == [['Sem ordem', 'false'], ['Ordens', 'false'], ['Ativos', 'false'], ['Planos', 'true']] and m.hash() == '#vis=planos',
         'navegação: um ícone Manutenção → tela de entrada MOD-MAN (destacado, sem subitens); o seletor da tela traz Sem ordem · Ordens · Ativos · Planos e #vis=planos abre a visão Planos', [mn, vs, m.hash()])
    # 2 · visão Planos: 10 planos, 4 ativos sem plano, PM-02 com 1 vencida
    sem = J("[...document.querySelectorAll('main button[aria-label^=\"Criar plano para\"]')].map(b=>b.innerText)") or []
    pl = m.linhas(0)
    m.ok(len(pl) == 10 and len(sem) == 4 and '1 vencida' in m.linha('PM-02'), f'Planos: 10 planos, 4 ativos sem plano, PM-02 com 1 vencida ({len(pl)}, {len(sem)})', m.linha('PM-02'))
    # 3 · paridade do vencimento JS × Python
    js = J("window.__man.manLinhas(window.__man.manGet()).filter(l=>l.s).map(l=>[l.pid,l.aid,l.sid,l.x.sit,l.x.prev])")
    py = sorted([x['pid'], x['aid'], x['sid'], x['sit'], x['prev']] for x in DM.linhas())
    m.ok(sorted(js) == py, f'vencimento: manVenc (JS) = vencimento() (Python) nos {len(py)} ativo × serviço')
    # 4 · Sem ordem: 2 vencidas, primária pelo estado
    m.ir('vis=semordem'); b = m.body()
    m.ok(m.man("window.__man.manSemOrdem(m).venc.filter(l=>l.x.sit==='Vencida').length") == 2 and 'GERAR ORDEM PREVENTIVA' in b.upper() and 'Gerar 3 ordens preventivas' in m.hdr(), 'Sem ordem: 2 vencidas · primária "Gerar 3 ordens preventivas"', m.hdr())
    # 5 · gerar sem duplicar
    n0 = m.man("Object.keys(m.oms).length"); m.clk('Gerar 3 ordens preventivas'); tt = m.toast()
    n1 = m.man("Object.keys(m.oms).length"); r = J("(()=>{ const M=window.__man; const c=M.manClone(M.manGet()); const x=M.manGerarTodas(c); return x.msg||''; })()")
    m.ok(all(x in tt for x in ('OM-0235', 'OM-0236', 'OM-0237')) and n1 == n0 + 3 and 'Nada a gerar' in r, f'gerar: 3 ordens; gerar de novo não duplica · {tt[:100]}', r)
    m.ok('Gerar' not in m.hdr(), 'Sem ordem: sem nada a gerar, a primária "Gerar" sai', m.hdr())
    # 6 · OM-0235: tarefas do plano e falta de peça trava a liberação
    m.ir('om=OM-0235'); p = m.pan()
    r = J("(()=>{ try{ const M=window.__man; M.manLiberar(M.manClone(M.manGet()),'OM-0235',false,'Otávio',{executante:'Zé',tempo:'4'}); return 'liberou'; }catch(e){ return e.message; } })()")
    m.ok(p.startswith('OM-0235 · Trator 03') and 'Falta peça' in p and 'Solicitar compra' in p and 'Filtro de óleo MF 4292' in r, 'OM-0235: Falta peça e liberar bloqueado (ponte "Solicitar compra")', [p[:80], r])
    m.bloco('Tarefas'); m.ok(m.pan().count('Sem resposta') == 5, 'OM-0235: 5 tarefas do plano, nenhuma respondida', m.pan().count('Sem resposta'))
    # 7 · OM-0234: conflito com a produção → Liberar mesmo assim (ponte até o 1b) → Zé inicia, responde, informa a leitura e conclui
    m.ir('om=OM-0234'); m.clk('Liberar mesmo assim', '#ma-painel'); a = m.toast()
    m.ok('liberad' in a and m.man("m.oms['OM-0234'].etapa") == 'Liberadas', 'OM-0234: conflito à vista; "Liberar mesmo assim" libera e reserva', a)
    m.ir('om=OM-0234', perfil='Zé'); m.clk('Iniciar serviço', '#ma-painel')
    p = m.pan(); m.ok('Falta:' in p and m.man("m.oms['OM-0234'].etapa") == 'Em execução', 'concluir exige as tarefas respondidas (o motivo à vista)', p[-160:])
    m.bloco('Tarefas'); m.responder('Feito'); m.setv('#om-leitura', '2900'); m.clk('Previsto (5 h)', '#ma-painel'); m.clk('Concluir serviço', '#ma-painel'); e2 = m.toast()
    m.ok('menor que a última' in e2 and m.man("m.oms['OM-0234'].etapa") == 'Em execução', 'concluir recusa leitura menor que a última', e2)
    m.setv('#om-leitura', '2995'); m.clk('Concluir serviço', '#ma-painel'); c = m.toast()
    m.ok('em conferência' in c and 'ciclo fechado' in c and '3.245 h' in c, f'concluir fecha o ciclo: próxima em 3.245 h', c[:160])
    # 8 · plano: Trator 02 volta a Em dia a partir da execução (horímetro não zera)
    m.ir('plano=PM-01', perfil='Otávio'); m.sem_erro('PM-01'); l = m.linha('a02') or m.J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Trator 02')>=0&&r.getClientRects().length); return r?r.innerText.replace(/\\s+/g,' '):'';})()")
    m.ok('Em dia' in l and '3.245 h' in l, f'PM-01: Trator 02 Em dia, próxima 3.245 h', l[:160])
    # 9 · publicar v4 não muda a ordem aberta (OM-0237 da v3 do PM-07)
    m.ir('plano=PM-07'); m.clk('Preventiva mensal', 'main'); m.setv('#sv_td', '2'); m.clk('Salvar', '#sv-painel'); r1 = m.toast()
    m.clk('Publicar v4'); m.clk('Publicar v4', '#ma-painel'); r2 = m.toast()
    o = J("(()=>{ const c=window.__man.manGet(); const o=c.oms['OM-0237']; return [o.ver,o.chk.length,c.planos['PM-07'].versao]; })()")
    m.ok('v4' in r1 and 'PM-07 v4 publicada' in r2 and 'OM-0237 segue na v3' in r2 and o == [3, 5, 4], f'publicar v4: OM-0237 segue na v3', [r1[:80], r2[:120], o])
    # 10 · leitura do abastecimento muda a situação; leitura menor vira troca de contador a confirmar
    def abast(aid, cont):
        m.ir('ativo=' + aid); m.clk('Registrar abastecimento'); m.clk('Sede · D-118', '#ma-painel')
        m.setv('#ab-vol', '150'); m.setv('#ab-leit', cont); m.clk('Beto', '#ma-painel'); m.clk('Registrar abastecimento', '#ma-painel'); return m.toast()
    a1 = abast('a04', '3530'); a2 = abast('cb01', '48100')
    m.ok('AB-1043' in a1 and 'Revisão 250 h: vence em breve' in a1 and 'troca de contador' in a2, 'abastecimento: 3.530 h deixa o Trator 04 vencendo em breve; 48.100 km < 48.200 km pede confirmação', [a1[:120], a2[:120]])
    m.ir('vis=ativos'); l4 = m.linha('a04'); lc = m.linha('cb01')
    m.ok('Vence em breve' in l4 and '3.530 h' in l4 and 'a confirmar' in lc and '48.200 km' in lc, 'Ativos: Trator 04 recalculado; comboio mantém 48.200 km com leitura a confirmar', [l4[:120], lc[:120]])
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_probe', 'manut'), exist_ok=True)   # a pasta da captura pode não existir (falha da ferramenta, não do teste)
    m.c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_probe', 'manut', 'ma_planos_test_fim.png'))
finally:
    rc = m.fim()
sys.exit(rc)
