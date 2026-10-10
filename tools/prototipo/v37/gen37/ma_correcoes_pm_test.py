# -*- coding: utf-8 -*-
"""Teste CDP das correções do passo 4 nos Planos de manutenção, na tela única MA (detalhe #plano=, PCM simplificado S1–S2):
base "vencimento programado" no fechamento do ciclo · atalho Criar plano deixa o ativo "Sem vínculo" (sem plano duplicado) ·
marco negativo recusado · ativo em dois planos com o mesmo serviço recusado no vínculo · inativar com vencida pede confirmação ·
F5 reabre o plano · Vincular ativo some sem candidatos · Esc e Tab no painel · editar nome.
Uso: python3 ma_correcoes_pm_test.py   (lê _render; zera o cenário em cada bloco)"""
import sys, time
from ma_lib import MA

m = MA(1440, 1100); J = m.J
try:
    # 1 · base "vencimento programado": próxima revisão conta do vencimento (20/09/2026 + 365 d), não da execução (23/09)
    m.ir('plano=PM-05', perfil='Otávio', limpa=True); m.sem_erro('MA · PM-05')
    m.clk('Revisão pré-plantio', 'main'); m.setv('#sv_base', 'prog'); m.clk('Salvar', '#sv-painel'); m.clk('Publicar v2'); m.clk('Publicar v2', '#ma-painel')
    m.ir('venc=PM-05|a06|s1'); m.clk('Gerar ordem preventiva', '#ma-painel'); g = m.toast()
    m.ir('om=OM-0235'); m.clk('Liberar', '#ma-painel'); m.clk('Liberar mesmo assim', '#ma-painel')
    m.ir('om=OM-0235', perfil='Zé'); m.clk('Iniciar serviço', '#ma-painel'); m.bloco('Tarefas'); m.responder('Feito')
    m.setv('#om-leitura', '890'); m.J("(()=>{const b=[...document.querySelectorAll('#ma-painel button')].find(b=>/^Previsto/.test(b.innerText.trim())); if(b) b.click();})()"); time.sleep(.3)
    m.clk('Concluir serviço', '#ma-painel'); c = m.toast()
    m.ok('OM-0235' in g and 'em 20/09/2027' in c and 'conta do vencimento programado' in c, 'base programada: próxima em 20/09/2027', [g[:80], c[:160]])
    # 2 · atalho Criar plano: o ativo sai de "Sem plano" e não duplica; o endereço passa a #plano=PM-11
    m.ir('vis=planos', perfil='Otávio', limpa=True); m.clk('Criar plano para Distribuidor 3 t'); p0 = J("(document.querySelector('#np-painel')||{}).innerText||''")
    m.clk('Salvar', '#np-painel'); s1 = m.toast(); h = m.hash()
    m.ir('ativo=a07'); l = m.body()
    m.ir('vis=planos'); sp = J("[...document.querySelectorAll('main button[aria-label^=\"Criar plano para\"]')].map(b=>b.innerText)") or []
    m.ok('Novo plano' in p0 and 'PM-11' in s1 and h == '#plano=PM-11' and 'Sem vínculo' in l and 'PM-11' in l and len(sp) == 3 and not any('Distribuidor' in x for x in sp),
         f'atalho Criar plano: Distribuidor fica Sem vínculo · Vincular ao PM-11 ({h}, {len(sp)} sem plano)', s1[:80])
    # 3 · marco negativo é recusado no vínculo
    m.ir('plano=PM-11'); m.clk('Incluir serviço'); m.setv('#sv_nome', 'Revisão 100 h'); m.setv('#sv_h', '100'); m.setv('#sv_tempo', '2'); m.setv('#sv_esp', 'Mecânico'); m.clk('Salvar', '#sv-painel')
    m.setv('#pm-tk-s1', 'Lubrificar pontos de graxa'); m.clk('Incluir tarefa', 'main')
    m.clk('Vincular ativo'); m.setv('#vk_data', '2026-09-01'); m.setv('#vk_leit', '-50'); m.clk('Salvar', '#vk-painel'); e = J("(document.querySelector('#vk-painel')||{}).innerText||''")
    m.ok('Zero ou mais.' in e and J("!!document.querySelector('#vk-painel')"), 'vincular: leitura negativa recusada no campo', e[-120:])
    m.setv('#vk_leit', '600'); m.clk('Salvar', '#vk-painel'); v1 = m.toast()
    m.ok('Distribuidor 3 t vinculado ao PM-11' in v1 and not J("!!document.querySelector('#vk-painel')"), 'vincular: leitura 600 aceita', v1[:100])
    # 4 · ativo em dois planos com o mesmo serviço: aviso no novo plano e vínculo recusado
    m.ir('vis=planos', perfil='Otávio', limpa=True); m.clk('Novo plano')
    m.setv('#np_nome', 'MF 7719 cópia'); m.setv('#np_tipo', 'modelo'); m.setv('#np_modelo', 'MF 7719'); av = J("(document.querySelector('#np-painel')||{}).innerText||''"); m.setv('#np_base', 'PM-01'); m.clk('Salvar', '#np-painel')
    m.clk('Vincular ativo'); m.setv('#vk_data', '2026-09-02'); m.setv('#vk_leit', '2793'); m.clk('Salvar', '#vk-painel'); e = J("(document.querySelector('#vk-painel')||{}).innerText||''")
    m.ok('Trator 02 já está no PM-01' in av and 'já faz Revisão 250 h pelo PM-01' in e, 'dois planos, mesmo serviço: aviso ao criar e vínculo recusado', [av[-120:], e[-160:]])
    J("(()=>{const b=document.querySelector('#vk-painel button[aria-label=Fechar]'); if(b) b.click();})()"); time.sleep(.3); m.clk('Descartar alterações', '#vk-painel')
    # 5 · inativar plano com vencida pede confirmação; Manter ativo não muda nada
    m.ir('plano=PM-02', perfil='Otávio', limpa=True); m.clk('⋯ Inativar plano'); a = J("[...document.querySelectorAll('main [role=alert]')].map(x=>x.innerText).join(' ')") or ''
    est = m.man("m.planos['PM-02'].estado"); m.clk('Manter ativo', 'main')
    m.ok('Inativar mesmo assim' in a and 'Trator 03' in a and est == 'Ativo' and m.man("m.planos['PM-02'].estado") == 'Ativo', 'inativar com vencida pede confirmação', a[:120])
    # 6 · F5 reabre o plano aberto pela linha
    m.ir('vis=planos'); m.abre('PM-04'); h = m.hash(); m.recarregar(); h2 = J("(document.querySelector('main h2')||{}).innerText||''")
    m.ok(h == '#plano=PM-04' and h2.startswith('PM-04'), f'F5 reabre o plano ({h})', h2[:60])
    # 7 · Vincular ativo some quando todos já estão vinculados
    m.ok(not J("[...document.querySelectorAll('main button')].some(b=>b.innerText.trim()==='Vincular ativo'&&b.getClientRects().length)"), 'PM-04: sem candidatos, sem botão Vincular ativo')
    # 8 · painel do serviço: Tab gira dentro; Esc fecha
    m.clk('Revisão 250 h', 'main'); time.sleep(.3)
    for _ in range(30): m.tecla('Tab', 'Tab', 9)
    dentro = J("!!(document.activeElement&&document.activeElement.closest('#sv-painel'))")
    m.tecla('Escape', 'Escape', 27); time.sleep(.4)
    m.ok(dentro and not J("!!document.querySelector('#sv-painel')"), f'painel do serviço: Tab preso ({dentro}) e Esc fecha')
    # 9 · editar nome
    m.clk('Editar plano'); m.setv('#np_nome', 'Pulverizador Uniport 3030 · revisões 250/500 h'); m.clk('Salvar', '#np-painel'); s9 = m.toast()
    m.ok('PM-04 salvo' in s9 and m.man("m.planos['PM-04'].nome") == 'Pulverizador Uniport 3030 · revisões 250/500 h', 'editar plano: nome salvo', s9[:80])
    m.sem_erro('fim')
finally:
    rc = m.fim()
sys.exit(rc)
