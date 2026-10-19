import sys, json, time, importlib.util
src,casos=sys.argv[1],sys.argv[2]; sp=importlib.util.spec_from_file_location('d2',src); m=importlib.util.module_from_spec(sp)
sys.path.insert(0,'/home/user/sp-camada-sintetica/tools/prototipo/v37/gen37'); sp.loader.exec_module(m)
C=json.load(open(casos)); mx=0; mxn=''; tot=0; mm=0
for c in C:
    t0=time.perf_counter(); r=m.repartir(c['Q'],c['cfgs'],c.get('pools') or {}); ms=(time.perf_counter()-t0)*1000; tot+=ms
    if ms>mx: mx=ms; mxn=c['nome']
    mm=max(mm,len(r['motivos']))
print(json.dumps({'n':len(C),'max_ms':round(mx),'caso':mxn[:60],'med_ms':round(tot/len(C)),'max_motivos':mm}))
