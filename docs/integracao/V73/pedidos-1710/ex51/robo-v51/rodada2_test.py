"""Contraprova da classificação real, sem iniciar o executor de navegador."""
import ast,pathlib,re
src=pathlib.Path(__file__).with_name('casos_criticos.py').read_text()
tree=ast.parse(src); funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('destino','classe')]
ctx={'re':re,'RECEIT':{'AG-01','AG-01det','AG-04','AG-04det'}}
exec(compile(ast.Module(body=funcs,type_ignores=[]),'<classificacao>','exec'),ctx)
assert ctx['classe']('MA',{'t':'SM-0147 da OS-0502','h':'SM.dc.html#SM-0147'},None)==(None,None)
assert ctx['classe']('MA',{'t':'OS-0502','h':'OS.dc.html#OS-0502'},None)[0]=='OM→OS'
assert ctx['classe']('OS',{'t':'Retirar no almoxarifado','h':'EST.dc.html'},None)==('OS→EST','outro')
print('PASS 3 contraprovas N3 da classificação real; sem navegador')
