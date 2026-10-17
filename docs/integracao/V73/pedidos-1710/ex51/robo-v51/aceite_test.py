import importlib.util, pathlib, tempfile, json
p=pathlib.Path(__file__).with_name('aceite.py'); spec=importlib.util.spec_from_file_location('gate',p);gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
with tempfile.TemporaryDirectory() as d:
    assert gate.avaliar(d,1,[])['estado']=='BLOQUEADO'
    req=[('OS→EST','entregar','OS-0424'),('OS→EST','entregar','OS-0425'),('OS→EST','devolver','OS-0417'),('OS→EST','saldo','OS-0418'),('OS→receituário','','OS-0504'),('OS→receituário','','OS-0508'),('receituário→OS','','VIS-051'),('receituário→OS','','VIS-052'),('Aprovações→OS','','IN-01'),('OM→OS','','OM-0233'),('OS→OM','','OS-0420'),('OS→OM','','OS-0431'),('OS→OM','','OS-0507'),('receituário→OS','','RA-0140')]
    cases=[{'percurso':g,'sub':s,'detalhe':id,'res':{'r':'navega','alvo':'RA-0140' if g=='OS→receituário' else 'OS-0502','abriu':True}} for g,s,id in req]
    a=pathlib.Path(d,'casos-criticos.json');b=pathlib.Path(d,'casos-criticos-endereco.json')
    def write(): a.write_text(json.dumps({'casos':cases}));b.write_text(json.dumps({'casos':[]}))
    write();assert gate.avaliar(d,0.95,[])['estado']=='PASSOU_MEDICAO'
    assert gate.avaliar(d,0.94,[])['estado']=='BLOQUEADO'
    assert gate.avaliar(d,1,[{'erro':'x'}])['estado']=='BLOQUEADO'
    cases[0]['res']['inconclusivo']=True;write();assert gate.avaliar(d,1,[])['estado']=='BLOQUEADO'
    cases.pop(0);write();assert gate.avaliar(d,1,[])['estado']=='BLOQUEADO'
print('PASS 6 contraprovas do portão; sem execução de navegador.')
