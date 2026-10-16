# -*- coding: utf-8 -*-
"""CD-02 · defeitos do verificador (10 verificações no Chrome): cultura renomeada continua padrão do 'Cadastrar cultivar';
'Cadastrar rendimento' salva na operação mostrada; selo 'Sem pendências' na cor de concluído; linha nova cabe no artboard."""
from cadc_lib import T
import time
t=T(); J=t.J
try:
    t.goto('CD-02.dc.html')
    t.chk('selo com pendências nasce amarelo', t.chipcor()=='yellow', t.chipcor())
    # defeito 2 · renomear a cultura padrão
    t.openrow(0,'Soja 3 cultivares'); t.fset('nome','Soja RR'); t.btn('Salvar'); time.sleep(.2)
    t.clk('Criar cultivar'); cu=t.fv('cult')
    t.fset('nome','X1'); t.fset('dias','110'); t.btn('Salvar'); time.sleep(.2)
    t.chk('cultura renomeada: o formulário mostra Soja RR e a cultivar X1 é salva nela, com o aviso próprio',
          cu=='Soja RR' and not t.isopen() and 'Salvo: X1 em Soja RR' in t.toast() and 'Soja RR 4 cultivares' in (t.rowtxt(0,'Soja RR') or '')
          and 'Semente de soja rr X1' in (t.rowtxt(0,'X1') or '') and not t.errs(), [cu,t.toast(),t.rowtxt(0,'Soja RR'),t.rowtxt(0,'X1'),t.alerts(),t.errs()])
    # 64 Z resolve a pendência de semente
    t.openrow(0,'64 Z'); t.btn('Salvar'); time.sleep(.2)
    # defeito 3 · Operação mostrada = operação salva
    t.clk('Operações e rendimentos'); time.sleep(.2); t.clk('Criar rendimento'); op=t.fv('op')
    for k,val in [('conj','Trator 05 + Pulverizador 2'),('modo','Informado'),('rend','10'),('maq','100'),('pess','1'),('fonte','Medição local'),('vig','2027-06-30')]: t.fset(k,val)
    t.btn('Salvar'); time.sleep(.2)
    t.chk('Cadastrar rendimento sem mexer em Operação salva em Pulverização',
          op=='Pulverização' and not t.isopen() and 'Pulverização rende 10,00 ha/h' in t.toast() and 'Pulverização 2 conjuntos Tratos culturais' in (t.rowtxt(0,'Pulverização') or ''),   # TABELAS-FOCO (06/10/2026): Processo em coluna própria
          [op,t.alerts(),t.toast(),t.rowtxt(0,'Pulverização')])
    # defeito 6 · selo resolvido em verde
    t.openrow(0,'Derriçadeiras'); t.fset('fonte','Medição local'); t.btn('Salvar'); time.sleep(.2)
    t.chk('sem pendências: selo "Sem pendências" na cor de concluído (verde)', 'Sem pendências' in t.header() and t.chipcor()=='green', [t.header(),t.chipcor()])
    # defeito 7 · operação + conjunto novos cabem no artboard
    t.clk('Criar rendimento'); t.fset('op','Outra operação…')
    for k,val in [('nop','Irrigação'),('conj','Pivô central 1'),('modo','Informado'),('rend','3'),('maq','50'),('pess','1'),('fonte','Medição local'),('vig','2027-06-30')]: t.fset(k,val)
    t.btn('Salvar'); time.sleep(.2); f1=t.folga(0,'Pivô central 1')
    t.chk('operação e conjunto novos aparecem inteiros no artboard (folga ≥ 20 px)', f1 is not None and f1>=20, f1)
    t.clk('Criar rendimento')
    for k,val in [('conj','Pivô central 2'),('modo','Informado'),('rend','3'),('maq','50'),('pess','1'),('fonte','Medição local'),('vig','2027-06-30')]: t.fset(k,val)
    t.fset('op','Irrigação'); t.btn('Salvar'); time.sleep(.2); f2=t.folga(0,'Pivô central 2')
    t.chk('ainda cabe mais um conjunto novo (folga ≥ 0 px)', f2 is not None and f2>=0, f2)
    t.clk('Culturas e cultivares'); time.sleep(.2); f3=t.folga(0)
    t.chk('aba Culturas com a cultivar nova também cabe', f3 is not None and f3>=20, f3)
    t.chk('nenhum erro de JS', not t.errs(), t.errs())
    t.shot('cadc_fix_cd02.png')
finally:
    t.fim()
