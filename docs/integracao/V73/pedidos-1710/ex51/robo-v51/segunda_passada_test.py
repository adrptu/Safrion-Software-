import importlib.util,pathlib
p=pathlib.Path(__file__).with_name('rodar.py');spec=importlib.util.spec_from_file_location('rodar51',p);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
base={'url':'OS#OS-0502','temDialogo':True,'dlg':'','h1':'OS-0502','selected':[]}
assert not r.chegada_estrita(base,'OS-0502','OS#OS-0502')
assert r.chegada_estrita(dict(base,temDialogo=False),'OS-0502','OS#OS-0502')
assert not r.chegada_estrita(dict(base,dlg='OS-0503'),'OS-0502','OS#OS-0502')
assert not r.chegada_estrita(dict(base,dlg='OS-0502'),'OS-0502','MA#OS-0502')
assert not r.chegada_estrita(dict(base,dlg='PC-0012 da OS-0502'),'OS-0502','OS#OS-0502')
assert not r.chegada_estrita(dict(base,dlg='OS-0502/2'),'OS-0502','OS#OS-0502')
assert r.chegada_estrita(dict(base,selected=['OS-0502 selecionada']),'OS-0502','OS#OS-0502')
print('PASS 7 casos da função real da segunda passada A3/A5/A6/A10; sem navegador.')
