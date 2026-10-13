# -*- coding: utf-8 -*-
"""CD-06 · defeitos do verificador (12 verificações no Chrome): item sem preço abre o campo vazio e salva sem preço (também a
semente vinda do CD-02); grupo padrão renomeado continua padrão do 'Cadastrar item'; selo 'Cadastro completo' na cor de concluído;
Local padrão acompanha o cadastro de locais (novo e renomeado)."""
from cadc_lib import T
import time, json
t=T(); J=t.J
try:
    t.goto('CD-06.dc.html')
    # a semente criada pelo CD-02 chega pelo armazenamento do navegador
    J("localStorage.setItem('talhao-os-cadastros-v1',JSON.stringify({sementes:['Semente de soja 64 Z']}))"); t.goto('CD-06.dc.html')
    # SOLO-01 (D-10): o Calcário dolomítico ganhou preço de referência e data; o item sem preço e o "Cadastro completo" usam só a semente do CD-02
    t.chk('abre com pendências no selo amarelo', '1 item sem preço · 1 item sem embalagem' in t.header() and t.chipcor()=='yellow', [t.header(),t.chipcor()])
    # defeito 1 · item sem preço
    t.openrow(0,'Semente de soja 64 Z'); pv=t.fv('preco'); t.btn('Salvar'); a=t.alerts()
    t.chk('semente do CD-02: preço abre vazio; só a embalagem é pedida', pv=='' and 'Informe quanto cabe' in a and 'número' not in a and 'data do preço' not in a, [pv,a])
    t.fset('cont','40'); t.btn('Salvar'); time.sleep(.2)
    t.chk('o item salva sem preço (campo vazio) e a linha diz "Sem preço"',
          not t.isopen() and 'sem preço de referência' in t.toast() and 'Sem preço' in (t.rowtxt(0,'Semente de soja 64 Z') or ''), [t.alerts(),t.toast(),t.rowtxt(0,'Semente de soja 64 Z')])
    t.openrow(0,'Semente de soja 64 Z'); t.fset('preco','12,5'); t.fset('pdata','2026-09-20'); t.btn('Salvar'); time.sleep(.2)
    t.chk('semente salva com embalagem e preço', not t.isopen() and 'R$ 12,50/kg' in (t.rowtxt(0,'Semente de soja 64 Z') or ''), [t.alerts(),t.rowtxt(0,'Semente de soja 64 Z')])
    # defeito 6 · selo resolvido
    t.chk('Cadastro completo no selo verde', 'Cadastro completo' in t.header() and t.chipcor()=='green', [t.header(),t.chipcor()])
    # defeito 2 · grupo padrão renomeado
    t.openrow(0,'Fertilizantes 11 itens'); t.fset('nome','Fertilizantes minerais'); t.btn('Salvar'); time.sleep(.2)
    t.clk('Cadastrar item'); g=t.fv('grupo'); t.fset('item','Sulfato de amônio'); t.fset('cont','50'); t.btn('Salvar'); time.sleep(.2)
    t.chk('grupo renomeado: o formulário mostra Fertilizantes minerais e o item é salvo nele, com o aviso próprio',
          g=='Fertilizantes minerais' and not t.isopen() and 'Salvo: Sulfato de amônio' in t.toast() and 'Fertilizantes minerais 12 itens' in (t.anyrow(0,'Fertilizantes minerais') or '')
          and not t.errs(), [g,t.alerts(),t.toast(),t.anyrow(0,'Fertilizantes minerais'),t.errs()])
    # defeito 8 · Local padrão acompanha os locais
    t.aba('Locais'); t.clk('Cadastrar local'); t.fset('nome','Galpão BV 2'); t.fset('faz','Boa Vista'); t.btn('Salvar'); time.sleep(.2)
    t.aba('Itens'); t.openrow(0,'MAP 11-52'); ops=t.fopts('local') or []; t.cancel()
    t.chk('local novo aparece em Local padrão do item', 'Galpão BV 2' in ops, ops)
    t.aba('Locais'); n0=t.rowtxt(0,'Galpão 1') or ''
    t.openrow(0,'Galpão 1'); t.fset('nome','Galpão Norte'); t.btn('Salvar'); time.sleep(.2); n1=t.rowtxt(0,'Galpão Norte') or ''
    t.openrow(0,'Galpão Norte'); dn=t.dlg(); t.cancel()
    # só o nome do local muda (1ª ocorrência): sem a coluna Capacidade (revisão TABR A4) o fim da linha "Galpão | 1" (tipo e itens) também lê "Galpão 1"
    t.chk('renomear o local leva os itens junto e o local segue protegido contra exclusão (causa no painel)',
          n0.replace('Galpão 1','Galpão Norte',1)==n1 and 'tem itens com este local padrão' in dn, [n0,n1,dn[-160:]])
    t.aba('Itens'); t.openrow(0,'NPK 20-05-20'); lv=t.fv('local'); ops=t.fopts('local') or []; t.cancel()
    t.chk('NPK 20-05-20 (em Galpão 1) passa a Galpão Norte e a lista não oferece mais Galpão 1', lv=='Galpão Norte' and 'Galpão 1' not in ops and 'Galpão Norte' in ops, [lv,ops])
    t.clk('Cadastrar item'); lv=t.fv('local'); t.cancel()
    t.chk('Local padrão do item novo continua Galpão 2', lv=='Galpão 2', lv)
    t.aba('Locais'); f=t.folga(0); t.aba('Itens')
    t.chk('com item e local novos, a tabela de locais cabe inteira no artboard (folga ≥ 20 px)', f is not None and f>=20, f)
    # sem padrão válido (Galpão 2 esvaziado e excluído), a lista mostra "Escolha…" e o salvar pede o local
    falhas=[]
    for it in ['KCl 60%','MAP 11-52','Nitrato de cálcio','Nitrato de potássio','Ureia 45%','Calcário dolomítico','Sulfato de amônio']:
        t.openrow(0,it); t.fset('local','Galpão Norte'); t.btn('Salvar')
        if t.isopen(): falhas.append((it,t.alerts())); t.cancel()
    t.aba('Locais'); t.delrow(0,'Galpão 2'); g2x=t.rowtxt(0,'Galpão 2'); t.aba('Itens'); t.clk('Cadastrar item'); lv=t.fv('local'); lt=J("(()=>{const i=document.querySelector('aside[role=dialog] select[id$=\"_local\"]'); return i?i.options[i.selectedIndex].text:null;})()")
    t.fset('item','Teste padrão'); t.fset('cont','1'); t.btn('Salvar'); a=t.alerts(); t.cancel()
    t.chk('Galpão 2 excluído: a lista do item novo mostra "Escolha…" e o salvar pede o local', not g2x and lv=='' and lt=='Escolha…' and 'Informe local padrão.' in a, [g2x,lv,lt,a,falhas])
    t.chk('nenhum erro de JS', not t.errs(), t.errs())
    t.shot('cadc_fix_cd06.png')
finally:
    t.fim()
