# -*- coding: utf-8 -*-
"""Verificador r3g · CD-01 · reativar Boa Vista e B1; B2 acima da área da fazenda; área total menor que os talhões."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
t0=time.time()
def P(*a): print(f'[{time.time()-t0:4.1f}s]',*a, flush=True)
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    s.openrow(1,'B1 Sequeiro'); s.fset('sit','Inativo'); s.btn('Salvar'); time.sleep(.3)
    s.openrow(0,'Boa Vista Boa Vista Ltda'); s.fset('sit','Inativa'); s.btn('Salvar'); time.sleep(.3); P('BV', s.rowtxt(0,'Boa Vista')[:40])
    P('open', s.openrow(0,'Boa Vista Inativa')); s.fset('sit','Ativa'); s.btn('Salvar'); time.sleep(.3); P('reativa BV', s.toast(), '|', s.alerts(), '| aberto', s.aberto()); P('BV faz', s.rowtxt(0,'Boa Vista')[:60])
    P('open', s.openrow(1,'B1 ')); s.fset('sit','Ativo'); s.btn('Salvar'); time.sleep(.3); P('reativa B1', s.toast(), '|', s.alerts()); P('B1', s.rowtxt(1,'B1 ')); P('BV g', s.rowtxt(1,'Boa Vista'))
    s.click('Cadastrar talhão','header'); s.fset('t','B2'); s.fset('faz','Boa Vista'); s.fset('decl','301'); s.btn('Salvar'); P('ALERT B2 301', s.alerts())
    s.fset('decl','300'); s.btn('Salvar'); time.sleep(.3); P('B2 salvo', s.aberto(), s.toast()); P('BV g', s.rowtxt(1,'Boa Vista'))
    P('open', s.openrow(0,'Boa Vista Boa Vista Ltda')); s.fset('area','419'); s.btn('Salvar'); P('ALERT area 419', s.alerts())
    P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
