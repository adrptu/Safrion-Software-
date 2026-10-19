# carrega dados2.repartir de <raiz>/tools/prototipo/v37/gen37/dados2.py; instr=True acrescenta só registro (como lib.js)
import sys,types
def _troca(t,a,b):
    n=t.count(a); assert n==1,(n,a[:70]); return t.replace(a,b)
def carrega(raiz,instr=False):
    g=raiz+'/tools/prototipo/v37/gen37'; src=open(g+'/dados2.py').read()
    if instr:
        src=_troca(src,"        for v0 in cs:\n            r=ext([v0],v0)\n            if r is not False: return r\n        return False\n",
                       "        for v0 in cs:\n            r=ext([v0],v0)\n            if r is not False: _BL.append((_PF[0],len(cs),r,st['passos'])); return r\n        _BL.append((_PF[0],len(cs),False,st['passos'])); return False\n")
        src=_troca(src,"    def grafo(V,pref,S):\n        n=len(V)\n","    def grafo(V,pref,S):\n        _PF[0]=pref; n=len(V)\n")
        if "lb=linha_bip(cf0,adj,V);" in src: src=_troca(src,"lb=linha_bip(cf0,adj,V);","lb=linha_bip(cf0,adj,V); _BL.append((_PF[0],len(cf0),'linhaBip',0)) if lb else None;")
        if "h=False   # MEDIÇÃO" in src: src=_troca(src,"h=False   # MEDIÇÃO","_BL.append((_PF[0],len(comp),'forçado',0)); h=False   # MEDIÇÃO")
    sys.path.insert(0,g)
    m=types.ModuleType('dados2_'+('i' if instr else 'n')); m.__file__=g+'/dados2.py'; m._BL=[]; m._PF=[None]
    exec(compile(src,g+'/dados2.py','exec'),m.__dict__); sys.path.pop(0); return m
def caminho(ms):
    est=any('combinações demais para conferir quem trabalha ao mesmo tempo' in x for x in ms); ci=any('máquinas compartilhadas em ciclo' in x for x in ms)
    return ('conservador (estouro e ciclo)' if ci else 'conservador (estouro do teto)') if est else ('conservador (ciclo ímpar)' if ci else 'cliques')
def resumo(r):
    return dict(alocado=r['alocado'],saldo=r['saldo'],deficit=r['deficit'],conflito=r['conflito'],pendente=r['pendente'],decorrido=r['decorrido'],hconj=r['hconj'],
                q=[x['q'] for x in r['itens']],h=[x['h'] for x in r['itens']],motivos=list(r['motivos']),caminho=caminho(r['motivos']))
