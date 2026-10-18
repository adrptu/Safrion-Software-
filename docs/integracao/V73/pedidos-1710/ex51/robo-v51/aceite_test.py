import hashlib
import importlib.util, pathlib, tempfile, json
p=pathlib.Path(__file__).with_name('aceite.py'); spec=importlib.util.spec_from_file_location('gate',p);gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
ok=dict(ids=.95,chegada=.95,volta=.95,voltar=.95)
with tempfile.TemporaryDirectory() as root:
    d=str(pathlib.Path(root,'saida'));pathlib.Path(d).mkdir()
    assert gate.avaliar(d,ok,[])['estado']=='BLOQUEADO'
    req=[('OS→EST','entregar','OS-0424'),('OS→EST','entregar','OS-0425'),('OS→EST','devolver','OS-0417'),('OS→EST','saldo','OS-0418'),('OS→receituário','','OS-0504'),('OS→receituário','','OS-0508'),('receituário→OS','','VIS-051'),('receituário→OS','','VIS-052'),('Aprovações→OS','','IN-01'),('OM→OS','','OM-0233'),('OS→OM','','OS-0420'),('OS→OM','','OS-0431'),('OS→OM','','OS-0507'),('receituário→OS','','RA-0140')]
    cases=[{'percurso':g,'sub':s,'detalhe':id,'res':{'r':'navega','de':'ORIGEM','telaDestino':'DESTINO','alvo':'RA-0140' if g=='OS→receituário' else 'OS-0502','abriu':True}} for g,s,id in req]
    a=pathlib.Path(d,'casos-criticos.json');b=pathlib.Path(d,'casos-criticos-endereco.json')
    pathlib.Path(d).parent.joinpath('v3.sha256').write_text('fixture de hashes')
    vinculo={'execucao':'teste','renderManifestSha256':hashlib.sha256(b'fixture de hashes').hexdigest()}
    pathlib.Path(d,'execucao-v51.json').write_text(json.dumps(vinculo))
    def write(): a.write_text(json.dumps({'vinculo':vinculo,'casos':cases}));b.write_text(json.dumps({'vinculo':vinculo,'casos':[]}))
    write();assert gate.avaliar(d,ok,[])['estado']=='PASSOU_MEDICAO'
    assert gate.avaliar(d,0.94,[])['estado']=='BLOQUEADO'
    assert gate.avaliar(d,ok,[{'erro':'x'}])['estado']=='BLOQUEADO'
    for metric in ok:
        bad=dict(ok);bad[metric]=0
        assert gate.avaliar(d,bad,[])['estado']=='BLOQUEADO',metric
    cases[0]['res']['r']='mesma tela';write()
    assert gate.avaliar(d,ok,[])['estado']=='BLOQUEADO'
    cases[0]['res']['r']='navega';cases[0]['res']['telaDestino']='ORIGEM';write()
    assert gate.avaliar(d,ok,[])['estado']=='BLOQUEADO'
    cases[0]['res']['telaDestino']='DESTINO'
    cases[0]['detalhe']='OS-0425 menciona OS-0424';write()
    assert gate.avaliar(d,ok,[])['estado']=='BLOQUEADO'
    cases[0]['detalhe']='OS-0424'
    cases.append({'percurso':'OS→EST','sub':'outro','res':{'r':'nada'}});write()
    assert gate.avaliar(d,ok,[])['estado']=='PASSOU_MEDICAO'
    cases.pop()
    old=json.loads(a.read_text());old['vinculo']={'execucao':'outra'};a.write_text(json.dumps(old))
    assert gate.avaliar(d,ok,[])['estado']=='BLOQUEADO'
    write()
    cases[0]['res']['inconclusivo']=True;write();assert gate.avaliar(d,ok,[])['estado']=='BLOQUEADO'
    cases.pop(0);write();assert gate.avaliar(d,ok,[])['estado']=='BLOQUEADO'
print('PASS 15 contraprovas do portão; sem execução de navegador.')
