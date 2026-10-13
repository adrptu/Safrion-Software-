# -*- coding: utf-8 -*-
"""CD-02 · culturas e operações cadastráveis (15 verificações no Chrome): abas com uma primária cada, árvore Cultura → cultivar,
formulário da cultura pela linha, 'Outra cultura…', item de semente vinculado, árvore Operação → conjunto, formulário da operação
(processo e atividades), 'Outra operação…' e rendimento por cultura."""
# TABELAS-FOCO (06/10/2026): processo, tipo de ciclo e unidade em colunas próprias; no CD-06, Unidade kg e Embalagem "—" em colunas próprias ('sem embalagem' segue no cabeçalho)
from cadc_lib import T
import time
t=T(); J=t.J
try:
    t.goto('CD-02.dc.html')
    t.chk('abre na aba Culturas com a primária "Cadastrar cultivar" (no bloco) e o estado das pendências',
          'Cadastrar cultivar' in t.bloco() and '1 cultivar sem semente · 1 premissa a validar' in t.header() and not t.errs(), t.header()+' '+t.errs())
    soja=t.rowtxt(0,'Soja 3 cultivares')
    t.chk('árvore Cultura → cultivar: Soja com unidade de produtividade e ciclo anual; coluna Registro saiu da tabela',
          soja and 'sc de 60 kg/ha' in soja and 'Anual' in soja and J("document.querySelector('[role=table]').innerText.indexOf('REGISTRO')<0"), soja)
    t.openrow(0,'Soja 3 cultivares')
    t.chk('linha da cultura abre o formulário da cultura (tipo de ciclo só consulta)',
          t.title()=='Cultura · Soja' and t.labels()==['Nome da cultura','Tipo de ciclo','Unidade de produtividade'] and t.fdis('tipo'), [t.title(),t.labels(),t.fdis('tipo')])
    t.cancel()
    # 64 Z: cultivar anual sem item de semente → salvar cria o item e resolve a pendência
    t.openrow(0,'64 Z'); pre=t.fv('sem'); t.btn('Salvar'); time.sleep(.2)
    t.chk('64 Z: salvar cria "Semente de soja 64 Z" (Produtos) e tira a pendência do cabeçalho',
          pre=='Criar item ao salvar' and 'Semente de soja 64 Z ›' in (t.rowtxt(0,'64 Z') or '') and 'criado em Produtos' in t.toast()
          and '1 cultivar sem semente' not in t.header(), [pre,t.rowtxt(0,'64 Z'),t.toast(),t.header()])
    t.openrow(0,'62 X'); t.fset('sem','Semente de milho AG 8700'); t.btn('Salvar'); a1=t.alerts()
    t.fset('sem','Semente de soja 58 W'); t.btn('Salvar'); a2=t.alerts()
    t.chk('semente da cultura errada ou já vinculada a outra cultivar é barrada junto ao campo',
          'Escolha uma semente de soja' in a1 and 'Semente de soja 58 W já é a semente da cultivar 58 W' in a2, [a1,a2])
    t.cancel()
    # Outra cultura…: cria a cultura sem sair do formulário da cultivar
    t.clk('Cadastrar cultivar'); t.fset('cult','Outra cultura…'); L=t.labels()
    t.fset('nome','BRS 373'); t.fset('ncult','Sorgo'); t.fset('tipo','Anual'); t.fset('unid','sc de 60 kg/ha'); t.fset('dias','120'); t.btn('Salvar'); time.sleep(.2)
    # TABELAS-FOCO (06/10/2026): tipo de ciclo e unidade de produtividade em colunas próprias na linha da cultura
    t.chk('"Outra cultura…" cria Sorgo com a cultivar BRS 373 e a semente vinculada',
          'Nome da nova cultura' in L and 'Tipo de ciclo' in L and not t.isopen() and 'Sorgo 1 cultivar Anual sc de 60 kg/ha' in (t.rowtxt(0,'Sorgo') or '')
          and 'Semente de sorgo BRS 373' in (t.rowtxt(0,'BRS 373') or ''), [L,t.rowtxt(0,'Sorgo'),t.rowtxt(0,'BRS 373'),t.alerts()])
    t.clk('Cadastrar cultivar'); t.fset('cult','Café'); L=t.labels()
    t.chk('cultura perene esconde ciclo em dias e semente; a lista Cultura já tem Sorgo',
          'Ciclo até a colheita' not in L and 'Item de semente' not in L and 'Sorgo' in (t.fopts('cult') or []), [L,t.fopts('cult')])
    t.fset('cult','Soja'); t.fset('nome','58 W'); t.fset('dias','118'); t.btn('Salvar')
    t.chk('cultivar repetida na mesma cultura é barrada', '58 W já está cadastrada em Soja' in t.alerts(), t.alerts())
    t.cancel()
    # ---- aba Operações e rendimentos ----
    t.clk('Operações e rendimentos'); time.sleep(.2)
    t.chk('aba Operações: primária "Cadastrar rendimento" e secundária "Comparar com o realizado"',
          'Cadastrar rendimento' in t.bloco() and J("document.body.innerText.indexOf('Comparar com o realizado')>=0 && document.body.innerText.indexOf('apontado')<0"), t.header())
    t.openrow(0,'Pulverização 1 conjunto Tratos culturais')   # processo em coluna própria (TABELAS-FOCO)
    t.chk('linha da operação abre processo (etapa de custo) e atividades usuais',
          t.title()=='Operação · Pulverização' and t.fv('proc')=='Tratos culturais' and 'Dessecação pré-plantio' in (t.fv('atvs') or ''), [t.title(),t.fv('proc'),t.fv('atvs')])
    t.fset('proc','Implantação'); t.btn('Salvar')
    t.chk('processo salvo aparece na linha da operação', 'Pulverização 1 conjunto Implantação' in (t.rowtxt(0,'Pulverização') or '') and 'atividades usuais' in t.toast(), [t.rowtxt(0,'Pulverização'),t.toast()])
    # Outra operação…: Calagem com o primeiro rendimento, só para soja
    t.clk('Cadastrar rendimento'); t.fset('op','Outra operação…'); L=t.labels()
    for k,val in [('nop','Calagem'),('nproc','Implantação'),('conj','Trator 03 + Distribuidor de calcário'),('cult','Soja'),('larg','12'),('vel','8'),('efic','70'),
                  ('maq','150'),('impl','60'),('pess','1'),('pess_rs','38'),('fonte','Ensaio da fazenda'),('vig','2027-06-30')]: t.fset(k,val)
    t.btn('Salvar'); time.sleep(.2)
    r=t.rowtxt(0,'Distribuidor de calcário') or ''
    t.chk('"Outra operação…" cria Calagem com o rendimento só para Soja (12 × 8 ÷ 10 × 70% = 6,72 ha/h)',
          'Nome da nova operação' in L and 'Calagem 1 conjunto Implantação' in (t.rowtxt(0,'Calagem') or '') and 'Soja' in r and '6,72 ha/h' in r and 'Operação Calagem cadastrada' in t.toast(), [L,t.rowtxt(0,'Calagem'),r,t.toast(),t.alerts()])
    t.clk('Cadastrar rendimento'); t.fset('op','Pulverização'); t.fset('conj','Trator 02 MF 7719 + Pulverizador PJ-3030 36 m'); t.fset('cult','Todas')
    for k,val in [('larg','36'),('vel','8'),('efic','75'),('maq','180'),('pess','1'),('vig','2027-06-30')]: t.fset(k,val)
    t.btn('Salvar'); a1=t.alerts(); t.fset('cult','Milho'); t.btn('Salvar'); time.sleep(.2)
    t.chk('mesmo conjunto na mesma operação: repetido para Todas é barrado; para Milho é aceito',
          'já tem rendimento em Pulverização para todas as culturas' in a1 and not t.isopen() and 'Pulverização 2 conjuntos Implantação' in (t.rowtxt(0,'Pulverização') or ''), [a1,t.alerts(),t.rowtxt(0,'Pulverização')])
    t.shot('cadc_cd02.png')
    t.goto('CD-06.dc.html'); r=t.rowtxt(0,'Semente de soja 64 Z') or ''
    t.chk('os itens criados pelas cultivares (64 Z e BRS 373) aparecem em Produtos › Sementes, pendentes de preço e embalagem',
          ' kg — ' in r and 'sem preço' in r.lower() and t.rowtxt(0,'Semente de sorgo BRS 373') and 'Sementes 6 itens' in (t.anyrow(0,'Sementes 6') or '')
          and '2 itens sem preço · 2 itens sem embalagem' in t.header(), [r,t.anyrow(0,'Sementes'),t.header()])   # SOLO-01 (D-10): o Calcário dolomítico tem preço (eram 3 itens sem preço)
    t.chk('nenhum erro de JS na jornada', not t.errs(), t.errs())
finally:
    t.fim()
