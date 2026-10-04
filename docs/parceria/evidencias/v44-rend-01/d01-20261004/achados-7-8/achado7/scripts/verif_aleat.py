# verifica as saídas aleatórias de cada variante (cache por entrada + saída idêntica); grava brutos/verif_aleat_<var>.jsonl
import sys,json,math,os
sys.path.insert(0,sys.path[0]); import verif
W=sys.argv[1]; L=json.load(open(W+'/entradas/aleatorias_s20261004.json')); cache={}
for n in sys.argv[2:]:
    out=open(W+f'/brutos/verif_aleat_{n}.jsonl','w'); nv=0
    for l in open(W+f'/brutos/aleat_js_{n}.jsonl'):
        s=json.loads(l); c=L[s['k']]; assert c['nome']==s['nome']
        key=(s['k'],json.dumps([round(x or 0,9) for x in s['q']]),round(s['saldo'],9))
        if key not in cache:
            try: v,th,mo=verif.verifica(c,s)
            except Exception as e: v,th,mo=['ERRO verificador: '+repr(e)],None,'erro'
            cache[key]=(v,None if th is None else ('inf' if th==math.inf else th),mo)
        v,th,mo=cache[key]; nv+=bool(v)
        out.write(json.dumps(dict(k=s['k'],cat=c['cat'],caminho=s['caminho'],violacoes=v,theta=th,motor=mo),ensure_ascii=False)+'\n')
    out.close(); print(n,'entradas com violação:',nv,flush=True)
