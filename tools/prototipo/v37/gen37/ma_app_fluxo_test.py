# -*- coding: utf-8 -*-
"""PCM simplificado S4 · app de campo × manutenção no Chrome (390 px; a tela MA a 1280 px), AC-PCM-27 e §3.7.
Fluxos: normal (Zé conclui a OM-0233 com teste e declara apto em 7 toques), recusa (Marcos não executa a OM; abastecimento sem
volume), sem sinal (fila do aparelho, uma vez só; OM mudada no escritório vira conflito que o Otávio aplica na tela MA),
repetição (duplo toque = um lançamento; reenvio não duplica), MB-04 Equipamento → achado em Sem ordem, 390 px sem rolagem lateral.
Uso (de gen37/, depois de build.py e montar_render.py): python3 ma_app_fluxo_test.py"""
import json, time
from app_lib import App

a = App([])
def go(t, w=1.1):
    a.c.goto(f'http://127.0.0.1:{a.p}/{t}', wait=w); a.J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(e.message));")
def cen(expr): return a.J(f"(()=>{{const c=window.__cen.cenGet(); return ({expr});}})()")
def man(expr): return a.J(f"(()=>{{const m=window.__man.manGet(); return ({expr});}})()")
def clkw(t, w=1.2):
    """toque num link que troca de tela: espera a nova tela"""
    r = a.clk(t); time.sleep(w); a.J("window.__errs=window.__errs||[]; if(!window.__errsOn){ window.__errsOn=1; window.addEventListener('error',e=>window.__errs.push(e.message)); }"); return r
def larg(): return a.J("document.documentElement.scrollWidth")
def toast(): return a.J("[...document.querySelectorAll('[role=status],[role=alert]')].map(x=>x.innerText).join(' | ')")
ERR = []
def errs(tela):
    e = a.erros() or []
    if e: ERR.append((tela, e))
try:
    a.c.size(390, 1800)
    # ---------- Marcos: Minha fila sem OM, cartão Máquina ----------
    go('MB-01.dc.html'); a.clk('Restaurar demonstração'); b = a.body()
    fila = b[b.find('Minha fila'):b.find('Abrir por tipo de trabalho')]
    a.ok('OM-0' not in fila and 'OS-0421' in fila and a.J("!!document.querySelector('a[href=\"MB-09.dc.html\"]')") and 'Marcos · operador · Santa Rita' in a.hdr(),
         'MB-01 Marcos: Minha fila só com O.S. (sem OM) e o cartão "Máquina" (MB-09) na vaga vazia')
    # ---------- (a) app · Zé conclui a OM-0233 com teste e declara apto: 7 toques ----------
    a.clk('Zé · mecânico'); b = a.body(); fila = b[b.find('Minha fila'):b.find('Abrir por tipo de trabalho')]
    a.ok('Zé · mecânico · Santa Rita' in a.hdr() and 'OM-0233' in fila and 'Teste pendente' in fila and a.foot() == 'Continuar serviço · OM-0233' and cen('c.app.usuario') == 'Zé',
         'Ver como Zé (c.app.usuario): a OM-0233 na Minha fila com "Teste pendente" e a primária "Continuar serviço · OM-0233"')
    n = 0; clkw('Continuar serviço'); n += 1; errs('MB-01')
    a.ok(a.J("location.pathname.endsWith('MB-09det.dc.html') && location.hash==='#OM-0233'") and 'OM-0233 · Trator T1' in a.hdr() and 'Não opere' in a.body(),
         'MB-09det: o painel da OM-0233 em 390 px, com "Não opere" no Trator T1 bloqueado')
    a.ok(larg() <= 390, f'MB-09det sem rolagem lateral a 390 px ({larg()} px)')
    a.clk('Aprovado'); n += 1; a.clk('Anexar foto e registrar Aprovado'); n += 1
    a.ok('2ª tentativa · Aprovado · foto (simulada)' in a.body() and cen("c.man.oms['OM-0233'].chk[3].tent.length") == 2, 'Teste: 2ª tentativa Aprovado com foto, gravada no cenário (só por acréscimo)')
    a.setv('#dp-leit', '4320'); n += 1; a.clk('Previsto (6,5 h)'); n += 1; a.clk('Concluir serviço'); n += 1
    a.ok(cen("c.man.oms['OM-0233'].etapa") == 'Em conferência' and a.foot() == 'Declarar Trator T1 apto', 'Concluir pela regra única: OM-0233 Em conferência e a primária vira "Declarar Trator T1 apto"')
    a.clk('Declarar Trator T1 apto'); n += 1
    a.ok(cen("c.man.ativos.a01.cond") == 'Apto' and 'Zé' in cen("c.man.oms['OM-0233'].aptidao.por") and a.foot() == 'Voltar à fila' and n == 7,
         f'(a) app: Trator T1 apto por Zé (responsável técnico) em {n} toques (especificado: 7)')
    errs('MB-09det')
    # ---------- recusa: Marcos vê a OM sem alterar; abastecimento sem volume ----------
    go('MB-01.dc.html'); a.clk('Restaurar demonstração'); go('MB-09det.dc.html#OM-0233'); b = a.body()
    a.ok(a.foot() == 'Voltar à fila' and 'Ação de Zé, executante' in b and 'Anexar foto' not in b and 'Concluir serviço' not in a.foot(),
         'recusa: Marcos abre a OM-0233 só para ver ("Ação de Zé, executante"); sem Concluir e sem teste')
    go('MB-09.dc.html'); n0 = cen('c.man.abast.length')
    a.ok('Trator 03 · MF 4292' in a.body() and 'Herdada do turno da OS-0421' in a.body() and a.foot() == 'Registrar abastecimento' and larg() <= 390,
         'MB-09 Marcos: Trator 03 herdado do turno da OS-0421, primária "Registrar abastecimento", 390 px sem rolagem lateral')
    a.clk('Comboio CB-01 · D-118'); a.clk('Registrar abastecimento')
    a.ok('volume em L' in toast() and cen('c.man.abast.length') == n0, 'recusa: sem volume o app diz o que falta e nada grava')
    # ---------- repetição: duplo toque no mesmo instante = um lançamento ----------
    a.setv('#mq-vol', '120'); a.setv('#mq-leit', '5126')
    a.J("(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.innerText.trim()==='Registrar abastecimento'&&/font-size: 17px/.test(x.getAttribute('style')||'')); b.click(); b.click(); return 1;})()"); time.sleep(.5)
    a.ok(cen('c.man.abast.length') == n0 + 1 and cen("c.man.ativos.a03.leit.val") == 5126, f'repetição: duplo toque em "Registrar abastecimento" grava 1 lançamento ({cen("c.man.abast.length") - n0})')
    errs('MB-09')
    # ---------- (e) app · abastecimento sem sinal: 6 toques; "Salvar e registrar outro"; volta do sinal uma vez só ----------
    go('MB-01.dc.html'); a.clk('Restaurar demonstração'); n0 = cen('c.man.abast.length')
    n = 0; clkw('Máquina'); n += 1; a.clk('Sem sinal')
    a.clk('Comboio CB-01 · D-118'); n += 1; a.setv('#mq-vol', '120'); n += 1; a.setv('#mq-leit', '5126'); n += 1; a.clk('Anexar foto (simulado)'); n += 1; a.clk('Registrar abastecimento'); n += 1
    a.ok(n == 6 and 'no aparelho' in toast() and cen('c.man.abast.length') == n0 and cen('c.app.manFila.length') == 1,
         f'(e) app sem sinal: {n} toques (especificado: 6); fica no aparelho e o servidor não muda')
    a.clk('Pulverizador PJ-3030'); a.clk('Comboio CB-01 · D-118'); a.setv('#mq-vol', '80'); a.setv('#mq-leit', '1550'); a.clk('Salvar e registrar outro')
    a.ok('Escolha a máquina' in a.body() and cen('c.app.manFila.length') == 2 and a.J("document.querySelector('#mq-vol')===null"),
         '"Salvar e registrar outro": 2º tíquete na fila e a tela limpa a máquina (fica só a data)')
    a.clk('Com sinal'); t1 = toast(); a.clk('Com sinal'); t2 = toast()
    a.ok(cen('c.man.abast.length') == n0 + 2 and cen('c.app.manFila.length') == 0 and '2 registros da manutenção enviados' in t1 and 'Já está com sinal' in t2,
         'volta do sinal: os 2 lançamentos entram uma vez só; tocar de novo não reenvia')
    errs('MB-09 sem sinal')
    # ---------- sem sinal + OM mudada no escritório = Conflito a resolver · Otávio ----------
    go('MB-01.dc.html'); a.clk('Restaurar demonstração'); a.clk('Zé · mecânico'); go('MB-09det.dc.html#OM-0233'); a.clk('Sem sinal')
    a.clk('Aprovado'); a.clk('Anexar foto e registrar Aprovado'); a.setv('#dp-leit', '4320'); a.clk('Previsto (6,5 h)'); a.clk('Concluir serviço')
    a.ok(cen("c.man.oms['OM-0233'].etapa") == 'Em execução' and cen('c.app.manFila.length') == 2 and '2 registros desta ordem no aparelho' in a.body(),
         'sem sinal: teste e conclusão ficam no aparelho (2 na fila); o servidor segue Em execução')
    r = a.J("window.__man.manMudar(null,(m)=>window.__man.manRetirada(m,'OM-0233',0,'Garantia','Concessionária Case IH','Otávio')).erro||''")
    a.clk('Com sinal'); t = toast(); time.sleep(.3)
    a.ok(r == '' and '2 conflitos a resolver' in t and cen("c.man.oms['OM-0233'].etapa") == 'Em execução' and cen("(c.man.appConf||[]).length") == 2 and 'Conflito a resolver · Otávio' in a.body(),
         'OM mudada no escritório: na volta os 2 registros viram "Conflito a resolver · Otávio" e nada é aplicado em silêncio')
    errs('MB-09det conflito')
    a.J("localStorage.setItem('safrion.perfilDemo','Otávio')"); a.c.size(1280, 900); go('MA.dc.html#om=OM-0233', 1.6)   # Ver como Otávio antes de abrir (trocar o perfil reabre a visão dele)
    a.ok(a.J("[...document.querySelectorAll('[role=alert]')].filter(x=>/Conflito a resolver · Otávio/.test(x.innerText)).length") == 2 and '1 ativo bloqueado' in a.body() and 'registros do app a resolver' in a.body(),
         'tela MA: o painel da OM-0233 mostra os 2 conflitos do app e o selo do cabeçalho conta os registros a resolver')
    a.clk('Aplicar registro do app'); a.clk('Aplicar registro do app')
    a.ok(man("m.oms['OM-0233'].etapa") == 'Em conferência' and man("(m.appConf||[]).filter(x=>x.estado==='A resolver').length") == 0 and not man("m.oms['OM-0233'].conflitoApp"),
         'Otávio aplica os registros sobre o estado de agora: OM-0233 Em conferência e o selo sai')
    errs('MA')
    # ---------- MB-04 Equipamento → achado em Sem ordem ----------
    a.c.size(390, 1800); go('MB-01.dc.html'); a.clk('Restaurar demonstração'); clkw('Ocorrência')
    a.setv('#oc_txt', 'Vazamento no comando da barra'); a.clk('Registrar ocorrência')
    a.ok('Escolha a máquina' in a.body() and not cen("Object.keys(c.man.achados).some(k=>c.man.achados[k].sint.indexOf('Vazamento no comando')>=0)"),
         'MB-04 Equipamento sem máquina: pede a máquina e nada grava')
    a.clk('Trator 03'); a.clk('Hidráulico'); a.clk('Com restrição'); a.clk('Registrar ocorrência'); b = a.body()
    a.ok('SM-0153 · Achado na Manutenção' in b and 'Na Manutenção · Sem ordem' in b and cen("c.man.achados['SM-0153'].os") == 'OS-0421' and cen("c.man.achados['SM-0153'].origem") == 'Relato' and larg() <= 390,
         'MB-04 Equipamento com máquina grava o achado SM-0153 (Relato, ligado à OS-0421) pela mesma função da tela MA')
    errs('MB-04')
    a.J("localStorage.setItem('safrion.perfilDemo','Otávio')"); a.c.size(1280, 900); go('MA.dc.html#vis=semordem', 1.6)
    a.ok('SM-0153' in a.body() and 'Vazamento no comando da barra' in a.body(), 'tela MA · Sem ordem: o SM-0153 vindo do app aparece para o Otávio decidir')
    errs('MA Sem ordem')
    a.ok(not ERR, 'sem erros JS nas telas ' + json.dumps(ERR, ensure_ascii=False)[:400])
    a.c.size(390, 1800); go('MB-01.dc.html'); a.clk('Restaurar demonstração')
finally:
    a.fim()
