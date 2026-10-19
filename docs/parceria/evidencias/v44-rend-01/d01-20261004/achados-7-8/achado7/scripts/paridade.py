# paridade JS × Python por caso: alocado, saldo, déficit, conflito, q (|Δ| ≤ 1e-9 relativo), motivos, caminho, resultado e passos do buraco
import json,sys
def ld(p): return [json.loads(l) for l in open(p) if l.strip() and not l.startswith('#')]
def cmp(j,p):
    e=[]
    for k in ('alocado','saldo','deficit'):
        if abs(j[k]-p[k])>1e-9*max(1,abs(j[k])): e.append(k)
    if j['conflito']!=p['conflito']: e.append('conflito')
    if max([abs((a or 0)-(b or 0)) for a,b in zip(j['q'],p['q'])]+[0])>1e-9*max(1,max(abs(a or 0) for a in j['q'])): e.append('q')
    if j['motivos']!=p['motivos']: e.append('motivos')
    if j['caminho']!=p['caminho']: e.append('caminho')
    jb=j.get('buraco',j.get('bl')); pb=p.get('buraco',p.get('bl'))
    norm=lambda L:[(b['grafo'],b['n'],b['buraco'],b['passos']) if isinstance(b,dict) else tuple(b) for b in L]
    if norm(jb)!=norm(pb): e.append('buraco')
    return e
if __name__=='__main__':
    J=ld(sys.argv[1]); P=ld(sys.argv[2]); pj={x['nome']:x for x in J}; n=0; bad=0
    for p in P:
        j=pj[p['nome']]; e=cmp(j,p); n+=1; bad+=bool(e)
        print(('IGUAL ' if not e else 'DIFERE '+','.join(e)+' ')+p['nome']+' | JS ms '+str(j.get('ms'))+' | Py ms '+str(p.get('ms')))
    print(f'# {n} casos, {bad} com diferença')
