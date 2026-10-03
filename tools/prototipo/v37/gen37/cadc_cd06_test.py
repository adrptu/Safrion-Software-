# -*- coding: utf-8 -*-
"""CD-06 · produtos, unidades e locais (15 verificações no Chrome): grupo cadastrável com natureza de custo, preço de referência com
data, embalagem estruturada, controle em um campo, situação Ativo/Inativo, unidade-base travada com motivo, locais com fazenda e
capacidade só em tanque e silo; o cabeçalho mostra pendência do cadastro (não do Estoque)."""
from cadc_lib import T
import time
t=T(); J=t.J
try:
    t.goto('CD-06.dc.html'); body=J("document.body.innerText")
    t.chk('abre com a pendência do cadastro no cabeçalho e sem fatos do Estoque (quarentena, pedido)',
          '1 item sem preço' in t.header() and 'Cadastrar item' in t.bloco() and 'quarentena' not in body and 'PC-088' not in body and not t.errs(), t.header())
    r=t.rowtxt(0,'KCl 60%'); t.openrow(0,'KCl 60%'); dk=t.dlg(); t.cancel()
    t.chk('item mostra unidade + embalagem, controle e preço com data; o saldo fica no painel com "Ver saldo no Estoque"',
          all(x in r for x in ['kg big bag de 1.000 kg','Só lote','R$ 2,40/kg','15/09/2026']) and 'Ver saldo no Estoque' in dk and 'Saldo: 50.000 kg' in dk, [r,dk[-200:]])
    t.openrow(0,'Herbicidas 5 itens'); ti=t.title(); nat=t.fv('nat')
    t.fset('nat','3.1.01 · Fertilizantes e corretivos'); t.btn('Salvar')
    t.chk('linha do grupo abre nome e natureza; a natureza salva aparece no grupo',
          ti=='Grupo · Herbicidas' and nat=='3.1.02 · Defensivos' and '5 itens · 3.1.01 · Fertilizantes e corretivos' in (t.rowtxt(0,'Herbicidas') or ''), [ti,nat,t.rowtxt(0,'Herbicidas'),t.toast()])
    t.openrow(0,'Glifosato 480'); d=t.dlg()
    t.chk('Glifosato: unidade-base travada com o motivo (saldo); embalagem galão de 20 L; preço em R$/L',
          t.fdis('un') and 'Travada: item com saldo de 1.200 L' in d and t.fv('emb')=='Galão' and t.fv('cont')=='20' and 'R$/L' in d and t.fv('ctrl')=='Lote e validade', d[:400])
    t.cancel()
    t.openrow(0,'Ureia 45%'); d=t.dlg()
    t.chk('Ureia sem saldo mas em plano: unidade travada pelo plano', t.fdis('un') and 'Travada: usado no plano Milho safrinha' in d, d[:300])
    t.cancel()
    t.openrow(0,'Calcário dolomítico'); L=t.labels(); t.fset('preco','480'); t.btn('Salvar'); a=t.alerts()
    t.chk('Calcário (granel): sem campo de conteúdo; preço sem data é barrado junto ao campo', 'Conteúdo da embalagem' not in L and 'Informe a data do preço.' in a, [L,a])
    t.fset('pdata','2026-09-20'); t.btn('Salvar'); time.sleep(.2)
    t.chk('preço salvo com data e a pendência some do cabeçalho', 'R$ 480,00/t' in (t.rowtxt(0,'Calcário') or '') and '20/09/2026' in (t.rowtxt(0,'Calcário') or '') and 'Cadastro completo' in t.header(), [t.rowtxt(0,'Calcário'),t.header()])
    t.openrow(0,'Calcário dolomítico'); t.fset('emb','Big bag'); L=t.labels(); d=t.dlg(); t.btn('Salvar'); a=t.alerts()
    t.chk('embalagem não granel pede o conteúdo na unidade-base (t)', 'Conteúdo da embalagem' in L and 'Informe quanto cabe em 1 big bag (em t).' in a, [L,a])
    t.cancel()
    t.openrow(0,'Fungicida C'); t.fset('sit','Inativo'); t.btn('Salvar'); time.sleep(.2)
    t.chk('inativar item em plano: chip Inativo e aviso de que sai dos planos e das cotações',
          'Inativo' in (t.rowtxt(0,'Fungicida C') or '') and 'sai dos planos e das cotações' in t.toast(), [t.rowtxt(0,'Fungicida C'),t.toast()])
    # Outro grupo…: cria o grupo no próprio formulário do item
    t.clk('Cadastrar item'); t.fset('grupo','Outro grupo…'); L=t.labels()
    for k,v in [('item','Trichoderma WP'),('ngrupo','Biológicos'),('nnat','3.1.02 · Defensivos'),('un','kg'),('emb','Saco'),('cont','1'),('ctrl','Lote e validade'),
                ('preco','85'),('pdata','2026-09-20'),('local','Câmara fria')]: t.fset(k,v)
    t.btn('Salvar'); time.sleep(.2)
    t.chk('"Outro grupo…" cria Biológicos (natureza 3.1.02) com o item Trichoderma WP',
          'Nome do novo grupo' in L and 'Natureza de custo' in L and 'Biológicos 1 item · 3.1.02 · Defensivos' in (t.rowtxt(0,'Biológicos') or '')
          and 'kg saco de 1 kg' in (t.rowtxt(0,'Trichoderma') or ''), [L,t.rowtxt(0,'Biológicos'),t.rowtxt(0,'Trichoderma'),t.alerts()])
    t.clk('Cadastrar item'); t.fset('item','MAP 11-52'); t.fset('cont','50'); t.btn('Salvar')
    t.chk('item repetido é barrado', 'Já existe o item MAP 11-52 em Fertilizantes.' in t.alerts(), t.alerts())
    t.cancel()
    t.aba('Locais')   # 01/10: locais numa aba própria do mesmo bloco (tabela 0 da aba); cabeçalho em caixa normal
    hd=J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' ').trim().toUpperCase())")
    t.chk('locais: fazenda na tabela, sem coluna Controle; capacidade só no tanque e no silo (do ativo)',
          any('FAZENDA' in h for h in hd) and not any('CONTROLE' in h for h in hd) and '15.000 L' in (t.rowtxt(0,'Tanque Sede') or '') and '60.000 sc 60 kg · ativo Silo 01' in (t.rowtxt(0,'Silo 01') or '')
          and '—' in (t.rowtxt(0,'Galpão 1') or ''), [hd,t.rowtxt(0,'Silo 01'),t.rowtxt(0,'Galpão 1')])
    t.chk('"Cadastrar local" é a ação da aba Locais (sem "+ Novo local")', J("document.body.innerText.indexOf('Novo local')<0") and t.clk('Cadastrar local')=='ok' and t.title()=='Cadastrar local', t.title())
    t.fset('nome','Galpão BV 2'); t.fset('faz','Boa Vista'); t.fset('tipo','Galpão'); t.btn('Salvar'); time.sleep(.2)
    t.chk('local novo na Boa Vista', 'Boa Vista' in (t.rowtxt(0,'Galpão BV 2') or '') and not t.errs(), [t.rowtxt(0,'Galpão BV 2'),t.errs()])
    t.shot('cadc_cd06.png')
finally:
    t.fim()
