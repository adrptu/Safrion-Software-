# -*- coding: utf-8 -*-
"""Verificação independente (CD-05): cenários além dos testes do implementador. Só imprime; quem lê confere.
CADUX (09/10/2026): reescrito sobre a seleção que abre detalhe (verif_cad_lib.py): o parceiro abre em consulta e "Editar parceiro" abre o
formulário; a cobertura é o item "Grupos de insumo" do mestre; "+ Criar parceiro" no cabeçalho. As partes de CD-02 e CD-01det, que
repetiam o verif_cad2.py, ficam só nele."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verif_cad_lib import V, out
PROBE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_probe')
v = V(); J = v.J
def cob(g):
    v.mestre('Grupos de insumo'); t = v.rowtxt(g); v.mestre('Todos'); return t
try:
    v.c.size(1440, 1100); v.ir('CD-05.dc.html')
    out('erro JS', J("(window.__errs||[]).join(' | ')"))
    out('cabeçalhos g_forn', v.cabecalhos())
    out('altura necessária', v.altura())
    v.c.shot(os.path.join(PROBE, 'verif_cd05_lista.png'))
    # origem da cobertura: o grupo abre em consulta (fonte: CD-06)
    v.mestre('Grupos de insumo'); v.abre('Sementes'); out('origem Sementes', v.painel()); out('  texto', (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '')[:300]); v.fecha(); v.mestre('Todos')
    # a) canal E-mail marcado sem e-mail (não homologado): salva? (compara com a regra do WhatsApp)
    v.clk('+ Criar parceiro'); v.fset('nome', 'Teste Email Vazio'); v.fset('cnpj', '11.222.333/0001-81'); v.marca('Cliente'); v.marca('E-mail'); v.btn('Salvar')
    out('E-mail autorizado sem e-mail, não homologado: painel', v.painel()); out('  alertas', v.alerts()); out('  linha', v.rowtxt('Teste Email Vazio'))
    v.fecha()
    v.clk('+ Criar parceiro'); v.fset('nome', 'Teste Whats Vazio'); v.fset('cnpj', '11.222.333/0001-81'); v.marca('Cliente'); v.marca('WhatsApp'); v.btn('Salvar')
    out('WhatsApp autorizado sem número: painel', v.painel()); out('  alertas', v.alerts())
    v.fecha()
    # b) desmarcar E-mail num não homologado com e-mail → "não autorizado" no e-mail
    v.edita('Coop Grão Sul'); v.marca('E-mail'); v.btn('Salvar'); v.fecha()   # o Coopergrão do roteiro antigo não existe mais no cenário (hoje: Coop Grão Sul)
    out('Coop Grão Sul sem E-mail autorizado', v.rowtxt('Coop Grão Sul'))
    # c) homologar F07 (só WhatsApp, sem e-mail)
    v.edita('Química Centro-Oeste'); v.fset('homol', 'Sim'); v.btn('Salvar')
    out('F07 homologar sem e-mail/sem canal', v.alerts())
    v.fset('email', 'vendas@quimicaco.com.br'); v.marca('E-mail'); v.btn('Salvar')
    out('F07 homologado: painel', v.painel()); out('  toast', v.toast()); v.fecha(); out('  Fungicidas', cob('Fungicidas'))
    # d) autorizar WhatsApp da Sementes Vale
    v.edita('Sementes Vale'); v.marca('WhatsApp'); v.btn('Salvar'); v.fecha()
    out('Sementes Vale com WhatsApp autorizado', v.rowtxt('Sementes Vale'))
    # e) CNPJ duplicado da Fertisul (doc exibido e cnpj antigo)
    v.clk('+ Criar parceiro'); v.fset('nome', 'Dup'); v.marca('Cliente'); v.fset('cnpj', '12.345.678/0001-95'); v.btn('Salvar')
    out('CNPJ igual ao exibido da Fertisul', v.alerts())
    v.fset('cnpj', '12.345.678/0001-95'); v.btn('Salvar')
    out('CNPJ antigo da Fertisul (dados2.cnpj / PT-07): painel', v.painel()); out('  alertas', v.alerts())
    v.fecha()
    # f) apagar WhatsApp de quem tem o canal autorizado
    v.edita('Fertisul'); v.fset('whats', ''); v.btn('Salvar')
    out('Fertisul sem número com WhatsApp autorizado', v.alerts()); v.fecha()
    # g) busca pelo CPF/CNPJ no mestre (a grade não tem busca própria)
    J("(()=>{const i=document.querySelector('#mx-q'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'12.345.678'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.5)
    out('busca "12.345.678" no mestre', [x[:60] for x in (v.linhas() or [])][:4])
    out('erro JS no fim', J("(window.__errs||[]).join(' | ')"))
    v.c.shot(os.path.join(PROBE, 'verif_cd05_fim.png'))
finally:
    v.fim()
