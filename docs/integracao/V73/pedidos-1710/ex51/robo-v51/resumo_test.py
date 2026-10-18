import tempfile,pathlib,json,subprocess,sys
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d);out=p/'out';out.mkdir();v3=p/'v3';v3.mkdir()
 (p/'ocultas.json').write_text('[]');(p/'navegacao.json').write_text('{"rows":[]}')
 source=(pathlib.Path(__file__).parent/'resumo.py').read_text();import ast
 tree=ast.parse(source);names=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PRINC' for t in n.targets))
 for n in names:(v3/(n+'.dc.html')).write_text('<html></html>')
 base=dict(r='navega',origem='detalhe',el={'t':'OS-0502','h':'OS.dc.html#OS-0502'},alvo='OS-0502',para='OS#OS-0503',abriu=False,destacou=False,titulo='OS-0503',voltar={})
 cases=[base,dict(base,alvo='',titulo='Outro'),dict(base,abriu=True,para='OS#OS-0502',titulo='OS-0502'),dict(base,r='mesma tela',abriu=True,empilhado={'abriu':True}),dict(base,abriu=True,empilhado={'abriu':True})]
 (out/'EST.v5.json').write_text(json.dumps({'screen':'EST','detalhes':[],'passagens':cases}))
 (out/'leva-check.json').write_text(json.dumps([{'tela':'EST','i':0,'dlg':'OS-0503','alvoNoCorpo':True,'tokNoCorpo':'OS 0502','alvoNoH1':True,'url':'OS#OS-0503'}]))
 (out/'OS.v5err.json').write_text('{"erro":"timeout"}')
 (p/'escopo-28.json').write_text('[{"resultado":"herda"},{"resultado":"inconclusivo"}]')
 subprocess.run([sys.executable,'-I',str(pathlib.Path(__file__).parent/'resumo.py'),str(out),str(p/'ocultas.json'),str(v3),str(p/'resumo.json')],check=True,capture_output=True)
 r=json.loads((p/'resumo.json').read_text())['robo'];assert r['navRegistro']==3 and r['chegou']==2 and r['empilhadosChegaramDona']==1 and r['inconclusivas']==1,r
 assert r['erros']==1 and r['escopo']['herda']==1,r
 result=json.loads((p/'resumo.json').read_text());assert result['aceite']['estado']=='BLOQUEADO'
 assert result['passagens'][1]['chegou'] is None and result['passagens'][1]['tipo']=='registro inconclusivo'
 print('PASS resumo: alvo errado e texto corporal da 2ª passada recusados; inconclusiva separada; controle positivo passa')
