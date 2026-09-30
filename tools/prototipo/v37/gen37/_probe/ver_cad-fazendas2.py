# -*- coding: utf-8 -*-
"""Verificador 2 · CD-01 · entidade Fazenda: edição pela linha, campos condicionais, fuso pela UF, validações, renomear, inativar."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess(); chk=L.chk
try:
    s.go('CD-01.dc.html')
    # 1 editar Boa Vista pela linha
    s.openrow(0,'Boa Vista'); a=s.aside(); lb=s.labels()
    chk('1 linha da Boa Vista abre o formulário com posse arrendada e campos do contrato', s.aberto() and s.fv('uf')=='MT' and s.fv('fuso')=='América/Cuiabá (UTC−4)' and 'Arrendador ou parceiro' in lb and 'Fim do contrato' in lb, [a[:300],lb, s.fv('fuso')])
    # 2 posse própria esconde contrato
    s.fset('posse','Própria'); lb=s.labels()
    chk('2 posse Própria esconde arrendador, fim e custo', not any(x in lb for x in ['Arrendador ou parceiro','Fim do contrato','Custo da terra']), lb)
    s.fset('posse','Arrendada'); lb=s.labels()
    chk('2b volta a Arrendada: campos voltam com valores', s.fv('arrend') or '', [s.fv('arrend'), s.fv('fim'), s.fv('custo')])
    # 3 contrato vencido
    s.fset('fim','2026-01-10'); s.btn('Salvar'); al=s.alerts()
    chk('3 contrato vencido barrado', 'Contrato vencido' in al, al)
    s.fset('fim','2029-08-31')
    # 4 área total menor que os talhões
    s.fset('area','100'); s.btn('Salvar'); al=s.alerts()
    chk('4 área total menor que os talhões ativos', 'somam 120' in al, al)
    s.fset('area','420')
    # 5 renomear e propagar
    s.fset('nome','Boa Vista II'); s.btn('Salvar'); time.sleep(.3)
    chk('5 renomear leva o nome aos talhões e ao estado', not s.aberto() and s.rowtxt(1,'Boa Vista II') is not None and 'Boa Vista II' in s.head(), [s.rowtxt(1,'Boa Vista II'), s.head(), s.toast()])
    s.openrow(1,'B1 Sequeiro'); chk('5b formulário do B1 mostra a fazenda renomeada', s.fv('faz')=='Boa Vista II', [s.fv('faz'), s.fopts('faz')])
    s.btn('Cancelar'); s.btn('Descartar alterações')
    # 6 nome duplicado (maiúsc/minúsc)
    s.click('+ Cadastrar fazenda'); s.fset('nome','santa rita'); s.btn('Salvar'); al=s.alerts()
    chk('6 nome duplicado barrado', 'Já existe a fazenda santa rita' in al, al)
    chk('6b fuso padrão de GO = São Paulo', s.fv('uf')=='GO' and s.fv('fuso')=='América/São Paulo (UTC−3)', [s.fv('uf'),s.fv('fuso')])
    s.fset('uf','AC'); f1=s.fv('fuso'); s.fset('uf','SP'); f2=s.fv('fuso')
    chk('6c UF AC → Rio Branco; SP → São Paulo', 'Rio Branco' in (f1 or '') and 'São Paulo' in (f2 or ''), [f1,f2])
    s.btn('Cancelar'); s.btn('Descartar alterações')
    # 7 inativar Santa Rita barrado
    s.openrow(0,'Santa Rita'); s.fset('sit','Inativa'); s.btn('Salvar'); al=s.alerts()
    chk('7 inativar fazenda com talhões ativos é barrado', 'Há 8 talhões ativos' in al, al)
    s.btn('Cancelar'); s.btn('Descartar alterações')
    # 8 parceria agrícola: rótulo, custo exibido na posse
    s.openrow(0,'Boa Vista II'); s.fset('posse','Parceria agrícola'); s.fset('custo','12'); s.btn('Salvar'); time.sleep(.3)
    chk('8 parceria salva e posse mostra custo', 'Parceria agrícola até 31/08/2029' in (s.rowtxt(0,'Boa Vista II') or '') and '12 sc/ha/ano' in (s.rowtxt(0,'Boa Vista II') or ''), s.rowtxt(0,'Boa Vista II'))
    # 9 documentos: preencher CAR e matrícula e limpar pendência → chip de estado muda
    s.openrow(0,'Boa Vista II'); s.fset('car','MT-5107925-ABCD'); s.fset('matr','5.555 · CRI de Sorriso'); s.fset('pend',''); s.btn('Salvar'); time.sleep(.3)
    chk('9 documentos em dia: coluna e estado do cabeçalho', 'CAR e matrícula' in (s.rowtxt(0,'Boa Vista II') or '') and 'documentos' not in s.head(), [s.rowtxt(0,'Boa Vista II'), s.head()])
    # 10 fazenda: persistência após recarregar
    s.go('CD-01.dc.html'); chk('10 recarregar mantém a fazenda renomeada e a posse', 'Parceria agrícola' in (s.rowtxt(0,'Boa Vista II') or '') and s.rowtxt(1,'Boa Vista II') is not None, [s.rowtxt(0,'Boa Vista II'), s.errs()])
    print('ERRS', s.errs(), 'OVF', s.overflow())
finally: s.close()
print('RES', sum(L.res), '/', len(L.res))
