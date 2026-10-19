import json,sys
a=[json.loads(l) for l in open(sys.argv[1])]; b=[json.loads(l) for l in open(sys.argv[2])]
assert len(a)==len(b),(len(a),len(b)); dif=0
for x,y in zip(a,b):
    ok=abs(x['alocado']-y['alocado'])<=1e-6*max(1,abs(x['alocado'])) and abs(x['saldo']-y['saldo'])<=1e-6*max(1,abs(x['saldo'])) and abs(x['deficit']-y['deficit'])<=1e-6*max(1,x['deficit']) and x['conflito']==y['conflito'] and all(abs(p-q)<=1e-6*max(1,abs(p)) for p,q in zip(x['q'],y['q'])) and x['motivos']==y['motivos']
    if not ok: dif+=1; print('DIF',x['i'],x['nome'][:50])
print('casos',len(a),'diferenças',dif)
