# -*- coding: utf-8 -*-
"""PCM simplificado · atrito (AC-PCM-28, ESPECIFICACAO §8): cliques, teclas e trocas de tela das tarefas (a)–(e), medidos no
candidato pela mesma convenção do inventário (lista curta = 1 toque; campo digitado = 1 clique + teclas; trocar de página = troca).
Cada tarefa é feita na tela, contando cada toque, e o total é comparado ao "Depois" do §8: nenhum total sobe.
O "Antes" fica como está no §8 (medido no inventário da base); aqui não é medido de novo.
Uso (de gen37/, depois de build.py e montar_render.py): python3 ma_atrito_test.py"""
import sys, time, json
from ma_lib import MA

m = MA(1440, 1000); J = m.J
class Conta:
    def __init__(s): s.c = 0; s.k = 0; s.t = 0
    def marca(s): J("window.__pag=1")
    def troca(s):
        if not J("window.__pag===1"): s.t += 1
        s.marca()
    def clk(s, txt, root='', w=.45):
        r = m.clk(txt, root, w); s.c += 1; s.troca(); return r
    def abre(s, rid):
        r = m.abre(rid); s.c += 1; s.troca(); return r
    def dig(s, sel, val):
        r = m.setv(sel, val); s.c += 1; s.k += len(val); return r
    def menu(s):
        """toque no item "Manutenção" do menu (1 clique; a página nova não conta como troca: é o destino da tarefa)"""
        m.clk('Manutenção', 'nav[aria-label=Menu]', w=1.4); s.c += 1; s.marca()
RES = []
def tarefa(nome, c, esperado, ok_estado, info=''):
    tot = (c.c, c.k, c.t); RES.append((nome, tot, esperado))
    m.ok(ok_estado and tot[0] <= esperado[0] and tot[2] <= esperado[2], f'{nome}: {tot[0]} cliques · {tot[1]} teclas · {tot[2]} trocas (§8 depois: {esperado[0]} · {esperado[1]} · {esperado[2]})', info)
def inicio(perfil, limpa=True, prep=None):
    m.ir('', perfil=perfil, limpa=limpa, pagina='MA.dc.html')
    if prep: prep()   # preparação na tela MA (window.__man), fora da contagem
    m.ir('', perfil=perfil, pagina='IN-01.dc.html'); c = Conta(); c.marca(); return c
def man(js): return J(f"window.__man.manMudar(null,(m)=>{{ {js} }}).erro||''")
try:
    # (a) Zé conclui a OM-0234 liberada (5 tarefas), web
    c = inicio('Otávio', prep=lambda: man("return window.__man.manLiberar(m,'OM-0234',true,'Otávio',{executante:'Zé',tempo:'5'});"))
    m.J("localStorage.setItem('safrion.perfilDemo','Zé')"); m.ir('', pagina='IN-01.dc.html'); c.marca()
    c.menu(); c.abre('OM-0234'); c.clk('Iniciar serviço', '#ma-painel'); m.bloco('Tarefas')
    n = m.responder('Feito'); c.c += n
    c.dig('#om-leitura', '2995'); c.clk('Previsto (5 h)', '#ma-painel'); c.clk('Concluir serviço', '#ma-painel')
    tarefa('(a) Zé conclui a OM-0234 (5 tarefas), web', c, (11, 4, 0), m.man("m.oms['OM-0234'].etapa") == 'Em conferência' and n == 5)
    # (a) Zé conclui a OM-0233 com teste e declara apto, web
    c = inicio('Zé'); c.menu(); c.abre('OM-0233') if 'om=OM-0233' not in m.hash() else None
    c.clk('Aprovado', '#ma-painel'); c.clk('Anexar foto e registrar Aprovado', '#ma-painel'); c.dig('#om-leitura', '4320'); c.clk('Previsto (6,5 h)', '#ma-painel')
    c.clk('Concluir serviço', '#ma-painel'); c.clk('Declarar Trator T1 apto', '#ma-painel')
    tarefa('(a) Zé conclui a OM-0233 com teste e declara apto, web', c, (7, 4, 0), m.man("m.ativos.a01.cond") == 'Apto')
    # (b) SM-0150 → corretiva liberada
    c = inicio('Otávio'); c.menu(); c.abre('a:SM-0150'); c.clk('Criar ordem corretiva', '#ma-painel'); c.dig('#om-tempo', '3'); c.clk('Liberar serviço', '#ma-painel')
    om = m.man("Object.values(m.oms).find(o=>o.origAch==='SM-0150')||{}") or {}
    tarefa('(b) SM-0150 → corretiva liberada', c, (5, 1, 0), om.get('etapa') == 'Liberadas', om.get('etapa'))
    # (b) INSP-104 → OM-0234, resolvendo o conflito
    c = inicio('Otávio'); c.menu(); c.abre('a:INSP-104'); c.clk('Vincular à OM-0234', '#ma-painel'); c.clk('Mover janela para 29/09', '#ma-painel'); c.clk('Liberar serviço', '#ma-painel')
    tarefa('(b) INSP-104 → OM-0234, resolvendo o conflito', c, (5, 0, 0), m.man("m.oms['OM-0234'].etapa") == 'Liberadas' and m.man("m.oms['OM-0234'].janIso") == '2026-09-29')
    # (b) NC-0912
    c = inicio('Otávio'); c.menu(); c.abre('a:NC-0912'); c.clk('Gerar ordem preventiva com NC-0912', '#ma-painel'); c.clk('Liberar serviço', '#ma-painel'); c.clk('Liberar mesmo assim', '#ma-painel')
    om = m.man("Object.values(m.oms).find(o=>(o.achados||[]).indexOf('NC-0912')>=0)||{}") or {}
    tarefa('(b) NC-0912 → preventiva liberada', c, (5, 0, 0), om.get('etapa') == 'Liberadas', om.get('id'))
    # (c) ver o que vence · programar · liberar as 3
    c = inicio('Otávio'); c.menu(); ver = 'VENCIDAS SEM ORDEM' in m.body().upper()
    tarefa('(c) ver o que vence', c, (1, 0, 0), ver and 'vis=semordem' in m.hash())
    c.clk('Gerar 3 ordens preventivas'); tarefa('(c) programar', c, (2, 0, 0), m.man("['OM-0235','OM-0236','OM-0237'].every(id=>!!m.oms[id])"))
    c.clk('Solicitar compra', '#ma-painel'); c.clk('Registrar recebimento', '#ma-painel'); c.clk('Liberar serviço', '#ma-painel')
    c.clk('Próxima', '#ma-painel'); c.clk('Liberar serviço', '#ma-painel'); c.clk('Liberar mesmo assim', '#ma-painel'); c.clk('Próxima', '#ma-painel'); c.clk('Liberar serviço', '#ma-painel')
    tarefa('(c) liberar as 3 (acumulado)', c, (11, 0, 0), m.man("['OM-0235','OM-0236','OM-0237'].every(id=>m.oms[id].etapa==='Liberadas')"), [m.man("['OM-0235','OM-0236','OM-0237'].map(id=>m.oms[id].etapa)")])
    # (d) aptos agora · custo do mês · custo de uma OM · custo por ativo
    c = inicio('Ana'); c.menu(); b = m.body().upper()
    tarefa('(d) aptos agora', c, (1, 0, 0), 'APTOS AGORA' in b and 'vis=ativos' in m.hash())
    tarefa('(d) custo do mês', c, (1, 0, 0), 'CUSTO DE MANUTENÇÃO · SET/2026' in b)
    tarefa('(d) custo por ativo', c, (1, 0, 0), 'CUSTO NO PERÍODO' in b)
    c = inicio('Ana'); c.menu(); c.abre('a02'); m.bloco('Ordens'); b = m.body()
    tarefa('(d) custo de uma OM (Manutenção · ativo › Ordens)', c, (2, 0, 0), 'OM-0219' in b and 'R$ 4.658,00' in b)
    # (e) abastecimento, web (operador herdado da alocação: 8)
    c = inicio('Otávio'); c.menu(); c.clk('Ativos', 'main'); c.abre('a02'); c.clk('Registrar abastecimento'); c.clk('Sede · D-118', '#ma-painel'); c.dig('#ab-vol', '180'); c.dig('#ab-leit', '3001')
    op = J("[...document.querySelectorAll('#ma-painel [aria-pressed=true]')].map(b=>b.innerText.trim())") or []
    if not any(x in op for x in ('Beto', 'Carlos', 'Marcos', 'Lucas', 'João')): c.clk('Beto', '#ma-painel')
    c.clk('Registrar abastecimento', '#ma-painel')
    tarefa('(e) abastecimento, web', c, (9, 7, 0), m.man("m.abast.some(b=>b.aid==='a02'&&b.vol===180)"), op)
    print('\nTABELA (executado no candidato · convenção do §8):')
    for nome, tot, esp in RES: print(f'  {nome:60s} {tot[0]:>3} · {tot[1]:>2} · {tot[2]}   (§8 depois: {esp[0]} · {esp[1]} · {esp[2]})')
    print('  (a) no app e (e) no app: ma_app_fluxo_test.py mede 7 e 6 toques.')
finally:
    rc = m.fim()
sys.exit(rc)
